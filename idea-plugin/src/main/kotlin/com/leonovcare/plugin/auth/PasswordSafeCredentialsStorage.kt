package com.leonovcare.plugin.auth

import com.intellij.credentialStore.CredentialAttributes
import com.intellij.credentialStore.Credentials
import com.intellij.credentialStore.generateServiceName
import com.intellij.ide.passwordSafe.PasswordSafe
import com.leonovcare.plugin.util.PlatformConstants

class PasswordSafeCredentialsStorage : CredentialsStorage {

    private fun accessTokenAttributes(): CredentialAttributes {
        return CredentialAttributes(generateServiceName(PlatformConstants.PLUGIN_ID, "access-token"))
    }

    private fun refreshTokenAttributes(): CredentialAttributes {
        return CredentialAttributes(generateServiceName(PlatformConstants.PLUGIN_ID, "refresh-token"))
    }

    private fun legacyTokenAttributes(): CredentialAttributes {
        return CredentialAttributes(generateServiceName(PlatformConstants.PLUGIN_ID, "api-token"))
    }

    override fun saveTokens(tokens: AuthTokens) {
        PasswordSafe.instance.set(accessTokenAttributes(), Credentials("access", tokens.accessToken))
        val refresh = tokens.refreshToken?.takeIf { it.isNotBlank() }
        if (refresh != null) {
            PasswordSafe.instance.set(refreshTokenAttributes(), Credentials("refresh", refresh))
        } else {
            PasswordSafe.instance.set(refreshTokenAttributes(), null)
        }
        // Cleanup old single-token key after migration.
        PasswordSafe.instance.set(legacyTokenAttributes(), null)
    }

    override fun getTokens(): AuthTokens? {
        val accessToken = (
            PasswordSafe.instance.get(accessTokenAttributes())?.getPasswordAsString()
                ?: PasswordSafe.instance.get(legacyTokenAttributes())?.getPasswordAsString()
            )?.trim()
                ?.takeIf { it.isNotBlank() }
                ?: return null

        val refreshToken = PasswordSafe.instance.get(refreshTokenAttributes())
            ?.getPasswordAsString()
            ?.trim()
            ?.takeIf { it.isNotBlank() }

        return AuthTokens(accessToken = accessToken, refreshToken = refreshToken)
    }

    override fun clearTokens() {
        PasswordSafe.instance.set(accessTokenAttributes(), null)
        PasswordSafe.instance.set(refreshTokenAttributes(), null)
        PasswordSafe.instance.set(legacyTokenAttributes(), null)
    }
}
