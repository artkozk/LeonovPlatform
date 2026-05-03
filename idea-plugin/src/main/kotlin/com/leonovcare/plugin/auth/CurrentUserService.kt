package com.leonovcare.plugin.auth

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.leonovcare.plugin.api.UserProfile
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map

@Service(Service.Level.APP)
class CurrentUserService {
    private val authService = AuthService.getInstance()

    fun currentUserFlow(): kotlinx.coroutines.flow.Flow<UserProfile?> = authService.state().map { it.userProfile }

    fun currentUser(): UserProfile? = authService.state().value.userProfile

    companion object {
        fun getInstance(): CurrentUserService =
            ApplicationManager.getApplication().getService(CurrentUserService::class.java)
    }
}
