package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.sync.SyncService

class SyncTasksAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        SyncService.getInstance(project).triggerManualSync()
    }
}

