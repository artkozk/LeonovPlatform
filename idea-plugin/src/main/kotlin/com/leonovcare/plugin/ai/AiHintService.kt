package com.leonovcare.plugin.ai

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.AiHintResponse
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.submission.SubmissionFileCollector
import com.leonovcare.plugin.task.CurrentTaskContext
import com.leonovcare.plugin.task.CurrentTaskService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import java.nio.file.Files

@Service(Service.Level.PROJECT)
class AiHintService(private val project: Project) {

    private val authService = AuthService.getInstance()
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val submissionCollector = SubmissionFileCollector()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun requestHintForCurrentTask(onResult: (Result<AiHintResponse>) -> Unit) {
        val context = currentTaskService.getCurrentTask()
            ?: return onResult(Result.failure(IllegalStateException(PlatformBundle.message("errors.taskUnavailable"))))

        if (authService.token() == null) {
            return onResult(Result.failure(IllegalStateException(PlatformBundle.message("errors.authRequired"))))
        }

        scope.launch {
            val result = runCatching {
                val sourceCode = loadSourceCode(context)
                authService.withAuthorizedToken { token ->
                    apiFactory.client().requestAiHint(token, context.task.id, sourceCode)
                        ?: throw IllegalStateException(PlatformBundle.message("errors.aiUnavailable"))
                }
            }.map { response ->
                if (response.hint.isBlank()) {
                    throw IllegalStateException(PlatformBundle.message("errors.aiEmptyResponse"))
                }
                response
            }
            onResult(result)
        }
    }

    private fun loadSourceCode(context: CurrentTaskContext): String {
        val mainFile = context.taskDir.resolve(context.details.mainFilePath).normalize()
        if (mainFile.startsWith(context.taskDir.normalize()) && Files.exists(mainFile)) {
            return Files.readString(mainFile)
        }

        val templateMain = context.template.files.firstOrNull()?.path?.let {
            context.taskDir.resolve(it).normalize()
        }
        if (templateMain != null && templateMain.startsWith(context.taskDir.normalize()) && Files.exists(templateMain)) {
            return Files.readString(templateMain)
        }

        return submissionCollector.collect(context.taskDir).joinToString(separator = "\n\n") { file ->
            "// ${file.path}\n${file.content}"
        }
    }

    companion object {
        fun getInstance(project: Project): AiHintService = project.getService(AiHintService::class.java)
    }
}
