package com.leonovcare.plugin.auth

interface PlatformAuthApi {
    suspend fun login(email: String, password: String): AuthTokens
    suspend fun refresh(refreshToken: String): AuthTokens
}
