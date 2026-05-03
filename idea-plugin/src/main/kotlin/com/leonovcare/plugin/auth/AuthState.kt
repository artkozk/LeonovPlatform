package com.leonovcare.plugin.auth

import com.leonovcare.plugin.api.UserProfile

data class AuthState(
    val authorized: Boolean,
    val userProfile: UserProfile? = null,
    val message: String? = null,
    val requiresReLogin: Boolean = false,
) {
    companion object {
        fun unauthorized(message: String? = null, requiresReLogin: Boolean = false): AuthState =
            AuthState(authorized = false, message = message, requiresReLogin = requiresReLogin)

        fun authorized(userProfile: UserProfile): AuthState = AuthState(authorized = true, userProfile = userProfile)
    }
}
