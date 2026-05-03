package com.leonovcare.plugin.submission

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.SubmissionClientInfo
import com.leonovcare.plugin.api.SubmissionRequest
import com.leonovcare.plugin.api.SubmissionResult
import com.leonovcare.plugin.api.SubmissionStatus
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.task.TaskManager
import com.leonovcare.plugin.api.PlatformApiClientFactory
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

@Service(Service.Level.PROJECT)
class SubmissionService(private val project: Project) {

    private val authService = AuthService.getInstance()
    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val taskManager = TaskManager.getInstance(project)
    private val fileCollector = SubmissionFileCollector()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val resultFlow = MutableStateFlow<SubmissionResult?>(null)

    fun latestResult(): StateFlow<SubmissionResult?> = resultFlow.asStateFlow()

    fun submitCurrentTask(onResult: (Result<SubmissionResult>) -> Unit) {
        if (authService.token() == null) return
        val context = currentTaskService.getCurrentTask() ?: return

        scope.launch {
            val result = runCatching {
                authService.withAuthorizedToken { token ->
                    val files = fileCollector.collect(context.taskDir)
                    val request = SubmissionRequest(
                        taskId = context.task.id,
                        language = context.details.language,
                        files = files,
                        client = SubmissionClientInfo(
                            pluginVersion = "0.1.0",
                            ideVersion = com.intellij.openapi.application.ApplicationInfo.getInstance().build.asString(),
                            platform = "IntelliJ IDEA",
                        ),
                        courseId = context.courseId,
                    )

                    val client = apiFactory.client()
                    val submission = client.submitSolution(token, context.task.id, request)
                    val finalResult = if (submission.status == SubmissionStatus.QUEUED || submission.status == SubmissionStatus.RUNNING) {
                        pollSubmission(client = client, token = token, taskId = context.task.id, attemptId = submission.attemptId)
                    } else {
                        submission
                    }

                    resultFlow.value = finalResult
                    taskManager.refreshAll()
                    finalResult
                }
            }
            onResult(result)
        }
    }

    private suspend fun pollSubmission(
        client: com.leonovcare.plugin.api.PlatformApiClient,
        token: String,
        taskId: String,
        attemptId: String,
    ): SubmissionResult {
        repeat(30) {
            val latest = client.getSubmissionResult(token, taskId, attemptId)
            if (latest.status !in setOf(SubmissionStatus.QUEUED, SubmissionStatus.RUNNING)) {
                return latest
            }
            delay(1000)
        }
        return SubmissionResult(
            attemptId = attemptId,
            status = SubmissionStatus.TIMEOUT,
            message = "Submission polling timeout",
        )
    }

    companion object {
        fun getInstance(project: Project): SubmissionService = project.getService(SubmissionService::class.java)
    }
}
