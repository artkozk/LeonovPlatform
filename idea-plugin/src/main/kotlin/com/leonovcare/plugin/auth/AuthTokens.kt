package com.leonovcare.plugin.auth

data class AuthTokens(
    val accessToken: String,
    val refreshToken: String? = null,
)
