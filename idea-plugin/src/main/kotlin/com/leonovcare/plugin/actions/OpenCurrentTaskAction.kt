package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.task.TaskManager

class OpenCurrentTaskAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val current = CurrentTaskService.getInstance(project).getCurrentTask() ?: return
        TaskManager.getInstance(project).openTask(current.task)
    }
}

