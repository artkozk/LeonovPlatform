package com.leonovcare.plugin.submission

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.SubmissionClientInfo
import com.leonovcare.plugin.api.SubmissionRequest
import com.leonovcare.plugin.api.SubmissionResult
import com.leonovcare.plugin.api.SubmissionStatus
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.task.TaskManager
import com.leonovcare.plugin.task.TaskFileService
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.util.PluginRuntimeInfo
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout
import java.util.concurrent.atomic.AtomicBoolean

@Service(Service.Level.PROJECT)
class SubmissionService(private val project: Project) {

    private val authService = AuthService.getInstance()
    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val taskManager = TaskManager.getInstance(project)
    private val taskFileService = TaskFileService()
    private val fileCollector = SubmissionFileCollector()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val resultFlow = MutableStateFlow<SubmissionResult?>(null)
    private val submissionInProgress = AtomicBoolean(false)
    private val submitRequestTimeoutMillis = 30_000L
    private val pollRequestTimeoutMillis = 20_000L

    fun latestResult(): StateFlow<SubmissionResult?> = resultFlow.asStateFlow()

    fun submitCurrentTask(onResult: (Result<SubmissionResult>) -> Unit) {
        if (!submissionInProgress.compareAndSet(false, true)) {
            onResult(Result.failure(IllegalStateException(PlatformBundle.message("errors.submissionInProgress"))))
            return
        }

        if (authService.token() == null) {
            submissionInProgress.set(false)
            onResult(Result.failure(IllegalStateException(PlatformBundle.message("errors.authRequired"))))
            return
        }

        val context = currentTaskService.getCurrentTask()
        if (context == null) {
            submissionInProgress.set(false)
            onResult(Result.failure(IllegalStateException(PlatformBundle.message("errors.taskUnavailable"))))
            return
        }

        scope.launch {
            val result = runCatching {
                authService.withAuthorizedToken { token ->
                    // Keep task workspace aligned with latest backend template before submit.
                    taskFileService.createOrUpdateTaskFiles(
                        project = project,
                        courseId = context.courseId,
                        details = context.details,
                        template = context.template,
                        overwriteExistingEditableFiles = false,
                        lessonMaterial = context.lessonMaterial,
                    )
                    val files = fileCollector.collect(context.taskDir)
                    val request = SubmissionRequest(
                        taskId = context.task.id,
                        language = context.details.language,
                        files = files,
                        client = SubmissionClientInfo(
                            pluginVersion = PluginRuntimeInfo.pluginVersion(),
                            ideVersion = com.intellij.openapi.application.ApplicationInfo.getInstance().build.asString(),
                            platform = PluginRuntimeInfo.idePlatformName(),
                        ),
                        courseId = context.courseId,
                    )

                    val client = apiFactory.client()
                    val submission = withTimeout(submitRequestTimeoutMillis) {
                        client.submitSolution(token, context.task.id, request)
                    }
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
            submissionInProgress.set(false)
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
            val latest = withTimeout(pollRequestTimeoutMillis) {
                client.getSubmissionResult(token, taskId, attemptId)
            }
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
