package com.leonovcare.plugin.auth

import com.leonovcare.plugin.api.UserProfile

interface AuthProvider {
    suspend fun authenticate(token: String): UserProfile
}
