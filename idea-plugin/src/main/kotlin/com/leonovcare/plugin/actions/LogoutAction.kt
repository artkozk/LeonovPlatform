package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.notifications.PlatformNotifications

class LogoutAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        AuthService.getInstance().logout()
        PlatformNotifications.authInfo(e.project, "Выход выполнен")
    }
}

