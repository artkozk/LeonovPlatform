package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.auth.LoginDialog
import com.leonovcare.plugin.notifications.PlatformNotifications

class LoginAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project
        val dialog = LoginDialog()
        if (!dialog.showAndGet()) return

        val request = dialog.request()
        val authService = AuthService.getInstance()

        if (request.useTokenAuth) {
            authService.loginWithToken(request.token) { result ->
                result.onSuccess {
                    PlatformNotifications.authInfo(project, "Вход выполнен")
                }.onFailure {
                    PlatformNotifications.authError(project, it.message ?: "Ошибка авторизации")
                }
            }
            return
        }

        if (request.email.isBlank() || request.password.isBlank()) {
            PlatformNotifications.authError(project, "Введите email и пароль")
            return
        }

        authService.loginWithCredentials(request.email, request.password) { result ->
            result.onSuccess {
                PlatformNotifications.authInfo(project, "Вход выполнен")
            }.onFailure {
                PlatformNotifications.authError(project, it.message ?: "Ошибка авторизации")
            }
        }
    }
}
