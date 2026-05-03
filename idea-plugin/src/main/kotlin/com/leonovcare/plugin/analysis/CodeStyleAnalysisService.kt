package com.leonovcare.plugin.analysis

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.CodeStyleItem
import com.leonovcare.plugin.api.CodeStyleResult
import com.leonovcare.plugin.api.Severity
import com.leonovcare.plugin.api.SubmissionClientInfo
import com.leonovcare.plugin.api.SubmissionRequest
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.settings.PlatformSettings
import com.leonovcare.plugin.submission.SubmissionFileCollector
import com.leonovcare.plugin.task.CurrentTaskService

@Service(Service.Level.PROJECT)
class LocalInspectionRunner {
    fun run(files: List<com.leonovcare.plugin.api.SubmissionFile>): CodeStyleResult {
        val issues = mutableListOf<CodeStyleItem>()
        files.forEach { file ->
            val lines = file.content.lines()
            lines.forEachIndexed { index, line ->
                if (line.contains("\t")) {
                    issues += CodeStyleItem(
                        severity = Severity.WARNING,
                        filePath = file.path,
                        line = index + 1,
                        column = 1,
                        message = "Tabs found. Prefer spaces.",
                        ruleId = "format.tabs",
                    )
                }
                if (line.length > 140) {
                    issues += CodeStyleItem(
                        severity = Severity.INFO,
                        filePath = file.path,
                        line = index + 1,
                        column = 141,
                        message = "Line is too long.",
                        ruleId = "format.line-length",
                    )
                }
                if (line.contains("import") && line.contains("*")) {
                    issues += CodeStyleItem(
                        severity = Severity.WARNING,
                        filePath = file.path,
                        line = index + 1,
                        column = 1,
                        message = "Avoid wildcard imports.",
                        ruleId = "imports.wildcard",
                    )
                }
            }
        }

        return CodeStyleResult(issues)
    }
}

@Service(Service.Level.PROJECT)
class CodeStyleAnalysisService(private val project: Project) {
    private val settings = PlatformSettings.getInstance()
    private val authService = AuthService.getInstance()
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val collector = SubmissionFileCollector()
    private val localRunner = LocalInspectionRunner()

    suspend fun analyzeCurrentTask(): CodeStyleResult {
        val context = CurrentTaskService.getInstance(project).getCurrentTask() ?: return CodeStyleResult(emptyList())
        val state = settings.mutableState()
        val files = collector.collect(context.taskDir)

        val local = if (state.enableLocalStyleAnalysis) {
            localRunner.run(files)
        } else {
            CodeStyleResult(emptyList())
        }

        if (!state.enableServerStyleAnalysis) {
            return local
        }

        if (authService.token() == null) return local

        val request = SubmissionRequest(
            taskId = context.task.id,
            language = context.details.language,
            files = files,
            client = SubmissionClientInfo(
                pluginVersion = "0.1.0",
                ideVersion = com.intellij.openapi.application.ApplicationInfo.getInstance().build.asString(),
                platform = "IntelliJ IDEA",
            ),
        )

        val server = runCatching {
            authService.withAuthorizedToken { token ->
                apiFactory.client().analyzeStyle(token, context.task.id, request)
            }
        }.getOrNull()

        return CodeStyleResult(local.items + (server?.items ?: emptyList()))
    }

    companion object {
        fun getInstance(project: Project): CodeStyleAnalysisService = project.getService(CodeStyleAnalysisService::class.java)
    }
}
