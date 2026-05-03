package com.leonovcare.plugin.auth

import com.leonovcare.plugin.api.UnauthorizedException
import com.leonovcare.plugin.api.UserProfile
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class AuthServiceTest {

    @Test
    fun `login with token saves token and updates state`() {
        val storage = InMemoryCredentialsStorage()
        val settings = InMemoryAuthSettingsBridge()
        val provider = TestAuthProvider(validTokens = setOf("valid-token"))
        val authApi = TestPlatformAuthApi()
        val service = AuthService(storage, provider, authApi, settings)

        val latch = CountDownLatch(1)
        var success = false

        service.loginWithToken("valid-token") {
            success = it.isSuccess
            latch.countDown()
        }

        assertTrue(latch.await(5, TimeUnit.SECONDS))
        assertTrue(success)
        assertEquals("valid-token", storage.storedTokens?.accessToken)
        assertEquals("student@example.com", settings.authEmail)
        assertTrue(service.state().value.authorized)
    }

    @Test
    fun `login with credentials saves access and refresh tokens`() {
        val storage = InMemoryCredentialsStorage()
        val settings = InMemoryAuthSettingsBridge()
        val provider = TestAuthProvider(validTokens = setOf("fresh-access"))
        val authApi = TestPlatformAuthApi(
            loginTokens = AuthTokens("fresh-access", "fresh-refresh"),
        )
        val service = AuthService(storage, provider, authApi, settings)

        val latch = CountDownLatch(1)
        var success = false

        service.loginWithCredentials("student@example.com", "password") {
            success = it.isSuccess
            latch.countDown()
        }

        assertTrue(latch.await(5, TimeUnit.SECONDS))
        assertTrue(success)
        assertEquals("fresh-access", storage.storedTokens?.accessToken)
        assertEquals("fresh-refresh", storage.storedTokens?.refreshToken)
        assertTrue(service.state().value.authorized)
    }

    @Test
    fun `withAuthorizedToken refreshes access token on 401`() = runBlocking {
        val storage = InMemoryCredentialsStorage(
            AuthTokens("expired-access", "refresh-1"),
        )
        val settings = InMemoryAuthSettingsBridge()
        val provider = TestAuthProvider(validTokens = setOf("fresh-access"))
        val authApi = TestPlatformAuthApi(
            refreshedTokens = AuthTokens("fresh-access", "refresh-2"),
        )
        val service = AuthService(storage, provider, authApi, settings)

        val value = service.withAuthorizedToken { token ->
            if (token == "expired-access") {
                throw UnauthorizedException("expired")
            }
            "ok-$token"
        }

        assertEquals("ok-fresh-access", value)
        assertEquals("fresh-access", storage.storedTokens?.accessToken)
        assertEquals("refresh-2", storage.storedTokens?.refreshToken)
    }

    @Test
    fun `logout clears token and settings`() {
        val storage = InMemoryCredentialsStorage(AuthTokens("valid-token", "refresh"))
        val settings = InMemoryAuthSettingsBridge().apply { authEmail = "student@example.com" }
        val provider = TestAuthProvider(validTokens = setOf("valid-token"))
        val authApi = TestPlatformAuthApi()
        val service = AuthService(storage, provider, authApi, settings)

        service.logout()

        assertNull(storage.storedTokens)
        assertNull(settings.authEmail)
        assertFalse(service.state().value.authorized)
    }

    private class InMemoryCredentialsStorage(
        var storedTokens: AuthTokens? = null,
    ) : CredentialsStorage {

        override fun saveTokens(tokens: AuthTokens) {
            this.storedTokens = tokens
        }

        override fun getTokens(): AuthTokens? = storedTokens

        override fun clearTokens() {
            storedTokens = null
        }
    }

    private class InMemoryAuthSettingsBridge : AuthSettingsBridge {
        var authEmail: String? = null
        var clearCalls = 0
        var clearWithCache = true

        override fun setAuthUserEmail(email: String?) {
            authEmail = email
        }

        override fun clearAuthState(clearLocalCache: Boolean) {
            clearCalls += 1
            clearWithCache = clearLocalCache
            authEmail = null
        }
    }

    private class TestAuthProvider(
        private val validTokens: Set<String>,
    ) : AuthProvider {
        override suspend fun authenticate(token: String): UserProfile {
            if (!validTokens.contains(token)) throw UnauthorizedException("invalid token")
            return UserProfile(
                id = "u1",
                email = "student@example.com",
                displayName = "Student",
            )
        }
    }

    private class TestPlatformAuthApi(
        private val loginTokens: AuthTokens = AuthTokens("login-access", "login-refresh"),
        private val refreshedTokens: AuthTokens = AuthTokens("refresh-access", "refresh-refresh"),
    ) : PlatformAuthApi {

        override suspend fun login(email: String, password: String): AuthTokens {
            if (email.isBlank() || password.isBlank()) {
                throw UnauthorizedException("invalid credentials")
            }
            return loginTokens
        }

        override suspend fun refresh(refreshToken: String): AuthTokens {
            if (refreshToken.isBlank()) {
                throw UnauthorizedException("missing refresh token")
            }
            assertNotNull(refreshToken)
            return refreshedTokens
        }
    }
}
