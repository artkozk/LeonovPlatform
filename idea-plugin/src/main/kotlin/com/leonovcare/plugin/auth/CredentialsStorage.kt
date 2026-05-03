package com.leonovcare.plugin.auth

interface CredentialsStorage {
    fun saveTokens(tokens: AuthTokens)
    fun getTokens(): AuthTokens?
    fun clearTokens()

    fun saveToken(token: String) {
        saveTokens(AuthTokens(accessToken = token, refreshToken = null))
    }

    fun getToken(): String? = getTokens()?.accessToken

    fun clearToken() {
        clearTokens()
    }
}
