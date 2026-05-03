package com.leonovcare.plugin.auth

import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.api.UserProfile

class TokenAuthProvider(
    private val clientFactory: PlatformApiClientFactory,
) : AuthProvider {
    override suspend fun authenticate(token: String): UserProfile {
        return clientFactory.client().getCurrentUser(token)
    }
}
