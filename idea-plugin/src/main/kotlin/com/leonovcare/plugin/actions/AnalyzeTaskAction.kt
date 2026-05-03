package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.leonovcare.plugin.analysis.CodeStyleAnalysisService
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.notifications.PlatformNotifications
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import javax.swing.SwingUtilities

class AnalyzeTaskAction : DumbAwareAction() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        scope.launch {
            runCatching { CodeStyleAnalysisService.getInstance(project).analyzeCurrentTask() }
                .onSuccess { result ->
                    SwingUtilities.invokeLater {
                        PlatformNotifications.taskInfo(project, PlatformBundle.message("status.styleIssues", result.items.size))
                    }
                }
                .onFailure {
                    SwingUtilities.invokeLater {
                        PlatformNotifications.taskError(project, it.message ?: PlatformBundle.message("status.analysisError"))
                    }
                }
        }
    }
}

