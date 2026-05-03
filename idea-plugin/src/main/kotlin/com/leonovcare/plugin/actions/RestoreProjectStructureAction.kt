package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.intellij.openapi.ui.Messages
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.project.ProjectRestoreService

class RestoreProjectStructureAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val answer = Messages.showYesNoDialog(
            project,
            "Восстановить структуру текущей задачи без перезаписи существующего решения?",
            "Восстановление структуры",
            "Восстановить",
            "Отмена",
            null,
        )
        if (answer != Messages.YES) return

        val result = ProjectRestoreService.getInstance(project).restoreCurrentTask(overwriteEditable = false)
        if (result.restored) {
            PlatformNotifications.taskInfo(project, result.message)
        } else {
            PlatformNotifications.taskError(project, result.message)
        }
    }
}

