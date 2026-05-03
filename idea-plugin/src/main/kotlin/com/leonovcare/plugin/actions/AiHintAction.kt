package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.ai.AiHintService
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.ui.AiHintDialog
import javax.swing.SwingUtilities

class AiHintAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        AiHintService.getInstance(project).requestHintForCurrentTask { result ->
            SwingUtilities.invokeLater {
                result.onSuccess { response ->
                    AiHintDialog(project, response).showAndGet()
                }.onFailure { error ->
                    PlatformNotifications.taskError(project, error.message ?: "AI hint failed")
                }
            }
        }
    }
}
