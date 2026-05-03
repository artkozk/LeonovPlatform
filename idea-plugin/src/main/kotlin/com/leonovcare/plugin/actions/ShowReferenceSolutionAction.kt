package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.ui.ReferenceSolutionViewer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import javax.swing.SwingUtilities

class ShowReferenceSolutionAction : DumbAwareAction() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val context = CurrentTaskService.getInstance(project).getCurrentTask() ?: return
        val authService = AuthService.getInstance()

        scope.launch {
            runCatching {
                authService.withAuthorizedToken { token ->
                    PlatformApiClientFactory.getInstance().client().getReferenceSolution(token, context.task.id)
                }
            }.onSuccess { reference ->
                SwingUtilities.invokeLater {
                    if (!reference.available) {
                        PlatformNotifications.taskInfo(project, reference.unavailableReason ?: "Эталон недоступен")
                    } else {
                        ReferenceSolutionViewer(project, reference).showAndGet()
                    }
                }
            }.onFailure {
                SwingUtilities.invokeLater {
                    PlatformNotifications.taskError(project, it.message ?: "Ошибка загрузки эталона")
                }
            }
        }
    }
}

