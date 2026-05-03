package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.submission.SubmissionResultPanel
import com.leonovcare.plugin.submission.SubmissionService

class SubmitTaskAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        SubmissionService.getInstance(project).submitCurrentTask { result ->
            result.onSuccess {
                PlatformNotifications.submissionInfo(project, "Проверка завершена: ${it.status}")
                SubmissionResultPanel(it).showAndGet()
            }.onFailure {
                PlatformNotifications.submissionError(project, it.message ?: "Ошибка проверки")
            }
        }
    }
}

