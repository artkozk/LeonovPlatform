package com.leonovcare.plugin.auth

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.leonovcare.plugin.api.ApiException
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.api.UnauthorizedException
import com.leonovcare.plugin.settings.PlatformSettings
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

interface AuthSettingsBridge {
    fun setAuthUserEmail(email: String?)
    fun clearAuthState(clearLocalCache: Boolean = true)
}

class PlatformSettingsBridge(
    private val settings: PlatformSettings,
) : AuthSettingsBridge {
    override fun setAuthUserEmail(email: String?) {
        settings.mutableState().authUserEmail = email
    }

    override fun clearAuthState(clearLocalCache: Boolean) {
        settings.mutableState().authUserEmail = null
        settings.mutableState().currentTaskId = null
        if (clearLocalCache) {
            settings.clearLocalCache()
        }
    }
}

@Service(Service.Level.APP)
class AuthService(
    private val credentialsStorage: CredentialsStorage,
    private val authProvider: AuthProvider,
    private val authApi: PlatformAuthApi,
    private val settingsBridge: AuthSettingsBridge,
) {

    constructor() : this(
        credentialsStorage = PasswordSafeCredentialsStorage(),
        authProvider = TokenAuthProvider(PlatformApiClientFactory.getInstance()),
        authApi = HttpPlatformAuthApi(PlatformSettings.getInstance()),
        settingsBridge = PlatformSettingsBridge(PlatformSettings.getInstance()),
    )

    private val logger = Logger.getInstance(AuthService::class.java)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val refreshMutex = Mutex()
    private val stateFlow = MutableStateFlow(AuthState.unauthorized())

    fun state(): StateFlow<AuthState> = stateFlow.asStateFlow()

    fun restoreSession() {
        val tokens = credentialsStorage.getTokens() ?: return
        scope.launch {
            runCatching {
                val validTokens = ensureValidTokens(tokens)
                val profile = authProvider.authenticate(validTokens.accessToken)
                settingsBridge.setAuthUserEmail(profile.email)
                stateFlow.value = AuthState.authorized(profile)
            }.onFailure {
                logger.warn("Session restore failed: ${it.message}")
                markSessionExpired("Session expired")
            }
        }
    }

    fun loginWithToken(token: String, onResult: (Result<Unit>) -> Unit) {
        scope.launch {
            val result = runCatching {
                val profile = authProvider.authenticate(token)
                credentialsStorage.saveTokens(AuthTokens(accessToken = token, refreshToken = null))
                settingsBridge.setAuthUserEmail(profile.email)
                stateFlow.value = AuthState.authorized(profile)
            }.onFailure {
                if (it is ApiException && it.statusCode == 401) {
                    stateFlow.value = AuthState.unauthorized(message = "Invalid token", requiresReLogin = true)
                } else {
                    stateFlow.value = AuthState.unauthorized(message = it.message)
                }
            }.map { Unit }
            onResult(result)
        }
    }

    fun loginWithCredentials(email: String, password: String, onResult: (Result<Unit>) -> Unit) {
        scope.launch {
            val result = runCatching {
                val tokens = authApi.login(email = email, password = password)
                val profile = authProvider.authenticate(tokens.accessToken)
                credentialsStorage.saveTokens(tokens)
                settingsBridge.setAuthUserEmail(profile.email)
                stateFlow.value = AuthState.authorized(profile)
            }.onFailure {
                if (it is ApiException && it.statusCode == 401) {
                    stateFlow.value = AuthState.unauthorized(message = "Invalid credentials", requiresReLogin = true)
                } else {
                    stateFlow.value = AuthState.unauthorized(message = it.message)
                }
            }.map { Unit }
            onResult(result)
        }
    }

    suspend fun <T> withAuthorizedToken(block: suspend (String) -> T): T {
        val storedTokens = credentialsStorage.getTokens() ?: throw UnauthorizedException("Not authorized")
        return try {
            block(storedTokens.accessToken)
        } catch (ex: UnauthorizedException) {
            val refreshed = refreshTokens(storedTokens)
            block(refreshed.accessToken)
        }
    }

    fun logout() {
        credentialsStorage.clearTokens()
        settingsBridge.clearAuthState(clearLocalCache = true)
        stateFlow.value = AuthState.unauthorized()
    }

    fun token(): String? = credentialsStorage.getTokens()?.accessToken

    private suspend fun ensureValidTokens(tokens: AuthTokens): AuthTokens {
        return try {
            authProvider.authenticate(tokens.accessToken)
            tokens
        } catch (ex: UnauthorizedException) {
            refreshTokens(tokens)
        }
    }

    private suspend fun refreshTokens(tokens: AuthTokens): AuthTokens {
        val refreshToken = tokens.refreshToken?.trim().orEmpty()
        if (refreshToken.isBlank()) {
            markSessionExpired("Session expired")
            throw UnauthorizedException("Refresh token is not available")
        }

        return refreshMutex.withLock {
            val latest = credentialsStorage.getTokens()
            val latestRefresh = latest?.refreshToken?.trim().orEmpty()
            if (latest != null && latest.accessToken != tokens.accessToken && latest.accessToken.isNotBlank()) {
                return@withLock latest
            }
            if (latestRefresh.isBlank()) {
                markSessionExpired("Session expired")
                throw UnauthorizedException("Refresh token is not available")
            }

            val refreshed = authApi.refresh(latestRefresh)
            credentialsStorage.saveTokens(refreshed)
            stateFlow.value = stateFlow.value.copy(requiresReLogin = false, message = null)
            refreshed
        }
    }

    private fun markSessionExpired(message: String) {
        credentialsStorage.clearTokens()
        settingsBridge.clearAuthState(clearLocalCache = false)
        stateFlow.value = AuthState.unauthorized(message = message, requiresReLogin = true)
    }

    companion object {
        fun getInstance(): AuthService = ApplicationManager.getApplication().getService(AuthService::class.java)
    }
}
