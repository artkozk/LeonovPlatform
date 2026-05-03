package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.run.TaskRunConfigurationService

class RunTaskAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        runCatching { TaskRunConfigurationService.getInstance(project).runCurrentTask(debug = false) }
            .onFailure { PlatformNotifications.taskError(project, it.message ?: "Run failed") }
    }
}

