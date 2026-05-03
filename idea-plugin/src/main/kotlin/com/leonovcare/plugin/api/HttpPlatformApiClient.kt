package com.leonovcare.plugin.api

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.intellij.openapi.diagnostic.Logger
import com.leonovcare.plugin.task.TaskLanguage
import com.leonovcare.plugin.task.TaskStatus
import com.leonovcare.plugin.task.TaskType
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Instant

class HttpPlatformApiClient(
    private val baseUrl: String,
    private val endpoints: PlatformEndpointMapping = PlatformEndpointMapping(),
) : PlatformApiClient {

    private val logger = Logger.getInstance(HttpPlatformApiClient::class.java)
    private val mapper: ObjectMapper = ObjectMapper()
        .registerModule(KotlinModule.Builder().build())
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)

    private val httpClient: HttpClient = HttpClient.newBuilder().build()

    override suspend fun getCurrentUser(token: String): UserProfile {
        val node = requestNode("GET", endpoints.me, token, retrySafe = true)
        val firstName = node.path("firstName").asText("").trim()
        val lastName = node.path("lastName").asText("").trim()
        val nickname = node.path("nickname").asText("").trim()
        val displayName = when {
            firstName.isNotBlank() || lastName.isNotBlank() -> "$firstName $lastName".trim()
            nickname.isNotBlank() -> nickname
            else -> node.path("email").asText("Student")
        }
        return UserProfile(
            id = node.path("id").asText(),
            email = node.path("email").asText(),
            displayName = displayName,
            avatarUrl = node.path("avatarUrl").takeUnless { it.isMissingNode || it.isNull }?.asText(),
        )
    }

    override suspend fun getCourses(token: String): List<Course> {
        val node = requestNode("GET", endpoints.courses, token, retrySafe = true)
        return node.path("items").map { item ->
            Course(
                id = item.path("id").asText(),
                title = item.path("title").asText(),
                description = item.path("description").asText(),
                progressPercent = item.path("progressPercent").asInt(0),
                tasksTotal = item.path("tasksTotal").asInt(0),
                tasksSolved = item.path("tasksSolved").asInt(0),
            )
        }
    }

    override suspend fun getCourseTasks(token: String, courseId: String): List<Task> {
        val coursePath = endpoint(endpoints.courseDetails, "courseId" to courseId)
        val courseNode = requestNode("GET", coursePath, token, retrySafe = true)
        val lessons = courseNode.path("lessons")

        val tasks = mutableListOf<Task>()
        var order = 1

        for (lesson in lessons) {
            val lessonId = lesson.path("id").asText()
            val lessonPath = endpoint(endpoints.lessonDetails, "lessonId" to lessonId)
            val lessonNode = requestNode("GET", lessonPath, token, retrySafe = true)
            val moduleId = lesson.path("moduleTitle").asText().ifBlank { lessonNode.path("lesson").path("moduleTitle").asText("") }

            lessonNode.path("tasks").forEach { taskNode ->
                val taskLanguage = TaskLanguage.fromApi(taskNode.path("language").asText("JAVA"))
                tasks += Task(
                    id = taskNode.path("id").asText(),
                    courseId = courseId,
                    moduleId = moduleId.ifBlank { null },
                    title = taskNode.path("title").asText(),
                    order = order++,
                    status = TaskStatus.NEW,
                    type = TaskType.fromApi(taskNode.path("type").asText("CONSOLE")),
                    language = taskLanguage.apiName,
                    locked = taskNode.path("locked").asBoolean(false),
                    unavailable = taskNode.path("unavailable").asBoolean(false),
                )
            }
        }

        return tasks
    }

    override suspend fun getTaskDetails(token: String, taskId: String): TaskDetails {
        val taskPath = endpoint(endpoints.taskDetails, "taskId" to taskId)
        val node = requestNode("GET", taskPath, token, retrySafe = true)
        val task = node.path("task")
        val examples = node.path("examples")
        val taskLanguage = TaskLanguage.fromApi(task.path("language").asText("JAVA"))

        val requirements = mutableListOf<String>()
        if (examples.isArray && examples.size() > 0) {
            requirements += "Use task examples to validate your solution."
        }

        return TaskDetails(
            id = task.path("id").asText(taskId),
            courseId = task.path("courseId").asText("unknown-course"),
            title = task.path("title").asText("Task"),
            statement = TaskStatement(
                format = StatementFormat.MARKDOWN,
                body = task.path("statementMd").asText(""),
                requirements = requirements,
            ),
            language = taskLanguage.apiName,
            type = TaskType.fromApi(task.path("type").asText("CONSOLE")),
            templateVersion = "1",
            entryPoint = task.path("entryPoint").asText(taskLanguage.defaultEntryPoint),
            mainFilePath = task.path("mainFilePath").asText(taskLanguage.defaultMainFilePath),
        )
    }

    override suspend fun getTaskTemplate(token: String, taskId: String): TaskTemplate {
        val templatePath = endpoint(endpoints.taskTemplate, "taskId" to taskId)
        return try {
            val node = requestNode("GET", templatePath, token, retrySafe = true)
            val files = node.path("files").map { file ->
                TaskTemplateFile(
                    path = file.path("path").asText(),
                    content = file.path("content").asText(),
                    editable = file.path("editable").asBoolean(true),
                )
            }
            TaskTemplate(taskId = taskId, files = files)
        } catch (ex: ApiException) {
            if (ex.statusCode !in listOf(404, 405)) {
                throw ex
            }
            val detailsNode = requestNode("GET", endpoint(endpoints.taskDetails, "taskId" to taskId), token, retrySafe = true)
            val taskNode = detailsNode.path("task")
            val language = TaskLanguage.fromApi(taskNode.path("language").asText("JAVA"))
            val starter = taskNode.path("starterCode").asText("")
            TaskTemplate(
                taskId = taskId,
                files = listOf(
                    TaskTemplateFile(
                        path = language.defaultMainFilePath,
                        content = starter,
                        editable = true,
                    )
                )
            )
        }
    }

    override suspend fun submitSolution(token: String, taskId: String, request: SubmissionRequest): SubmissionResult {
        val sourceCode = request.files.firstOrNull()?.content.orEmpty()
        val payload = mapper.writeValueAsString(
            mapOf(
                "sourceCode" to sourceCode,
                "language" to request.language,
                "files" to request.files.map { file ->
                    mapOf(
                        "path" to file.path,
                        "content" to file.content,
                    )
                },
                "client" to mapOf(
                    "pluginVersion" to request.client.pluginVersion,
                    "ideVersion" to request.client.ideVersion,
                    "platform" to request.client.platform,
                ),
            )
        )
        val node = requestNode("POST", endpoint(endpoints.taskSubmission, "taskId" to taskId), token, payload)

        return SubmissionResult(
            attemptId = node.path("submissionId").asText(),
            status = mapSubmissionStatus(node.path("status").asText("queued")),
            message = node.path("status").asText("queued"),
            createdAt = Instant.now(),
        )
    }

    override suspend fun getSubmissionResult(token: String, taskId: String, attemptId: String): SubmissionResult {
        val path = endpoint(endpoints.submissionStatus, "submissionId" to attemptId)
        val node = requestNode("GET", path, token, retrySafe = true)

        val compileOutput = node.path("compileOutput").asText("")
        val runLog = node.path("runLog").asText("")
        val feedback = node.path("feedback").asText("")

        val tests = mutableListOf<TestResult>()
        if (compileOutput.isNotBlank()) {
            tests += TestResult(
                name = "Compile",
                status = TestResultStatus.ERROR,
                message = compileOutput,
                errorOutput = compileOutput,
            )
        }
        if (runLog.isNotBlank()) {
            tests += TestResult(
                name = "Run",
                status = TestResultStatus.FAILED,
                message = runLog,
                output = runLog,
            )
        }

        return SubmissionResult(
            attemptId = node.path("id").asText(attemptId),
            status = mapSubmissionStatus(node.path("status").asText("queued")),
            score = node.path("score").asInt(0),
            maxScore = 100,
            message = feedback,
            testResults = tests,
            createdAt = parseInstant(node.path("createdAt").asText()),
            completedAt = Instant.now(),
        )
    }

    override suspend fun analyzeStyle(token: String, taskId: String, request: SubmissionRequest): CodeStyleResult? {
        val payload = mapper.writeValueAsString(
            mapOf(
                "taskId" to request.taskId,
                "language" to request.language,
                "files" to request.files,
            )
        )
        return try {
            val node = requestNode("POST", endpoint(endpoints.taskStyleCheck, "taskId" to taskId), token, payload)
            val items = node.path("items").map {
                CodeStyleItem(
                    severity = when (it.path("severity").asText("INFO").uppercase()) {
                        "ERROR" -> Severity.ERROR
                        "WARNING" -> Severity.WARNING
                        else -> Severity.INFO
                    },
                    filePath = it.path("filePath").asText(""),
                    line = it.path("line").asInt(0),
                    column = it.path("column").asInt(0),
                    message = it.path("message").asText(""),
                    ruleId = it.path("ruleId").asText(""),
                    quickFixAvailable = it.path("quickFixAvailable").asBoolean(false),
                )
            }
            CodeStyleResult(items)
        } catch (ex: ApiException) {
            if (ex.statusCode in listOf(404, 405)) {
                null
            } else {
                throw ex
            }
        }
    }

    override suspend fun getReferenceSolution(token: String, taskId: String): ReferenceSolution {
        return try {
            val path = endpoint(endpoints.taskReferenceSolution, "taskId" to taskId)
            val node = requestNode("GET", path, token, retrySafe = true)
            val files = node.path("files").map { file ->
                ReferenceSolutionFile(
                    path = file.path("path").asText(),
                    content = file.path("content").asText(),
                )
            }
            ReferenceSolution(
                taskId = taskId,
                files = files,
                explanation = node.path("explanation").asText(null),
                available = node.path("available").asBoolean(true),
                unavailableReason = node.path("unavailableReason").asText(null),
            )
        } catch (ex: ApiException) {
            if (ex.statusCode == 403 || ex.statusCode == 404) {
                ReferenceSolution(
                    taskId = taskId,
                    files = emptyList(),
                    available = false,
                    unavailableReason = "Reference solution is unavailable",
                )
            } else {
                throw ex
            }
        }
    }

    override suspend fun requestAiHint(token: String, taskId: String, sourceCode: String): AiHintResponse? {
        val payload = mapper.writeValueAsString(
            mapOf(
                "taskId" to taskId,
                "sourceCode" to sourceCode,
            )
        )
        return try {
            val node = requestNode("POST", endpoints.aiTaskHint, token, payload)
            val usageNode = node.path("usage")
            AiHintResponse(
                status = node.path("status").asText("ok"),
                hint = node.path("hint").asText(""),
                model = node.path("model").asText("").ifBlank { null },
                usage = if (usageNode.isMissingNode || usageNode.isNull) {
                    null
                } else {
                    AiHintUsage(
                        promptTokens = usageNode.path("promptTokens").asInt(0),
                        completionTokens = usageNode.path("completionTokens").asInt(0),
                        totalTokens = usageNode.path("totalTokens").asInt(0),
                    )
                },
            )
        } catch (ex: ApiException) {
            if (ex.statusCode in listOf(404, 405)) {
                null
            } else {
                throw ex
            }
        }
    }

    override suspend fun resetProgress(token: String, taskId: String): Boolean {
        return try {
            requestNode("POST", endpoint(endpoints.taskProgressReset, "taskId" to taskId), token, "{}")
            true
        } catch (ex: ApiException) {
            ex.statusCode !in listOf(404, 405)
        }
    }

    override suspend fun sync(token: String): SyncResult {
        return try {
            val node = requestNode("POST", endpoints.sync, token, "{}")
            SyncResult(
                updatedTasks = node.path("updatedTasks").asInt(0),
                changedStatuses = node.path("changedStatuses").asInt(0),
                unlockedTasks = node.path("unlockedTasks").asInt(0),
                serverTime = parseInstant(node.path("serverTime").asText()) ?: Instant.now(),
                errors = node.path("errors").map { it.asText() },
            )
        } catch (ex: ApiException) {
            if (ex.statusCode in listOf(404, 405)) {
                SyncResult(0, 0, 0, Instant.now(), listOf("Sync endpoint is not available"))
            } else {
                throw ex
            }
        }
    }

    override suspend fun markTaskInProgress(token: String, taskId: String): Boolean {
        return true
    }

    private suspend fun requestNode(
        method: String,
        path: String,
        token: String,
        payload: String? = null,
        retrySafe: Boolean = false,
    ): JsonNode {
        return withContext(Dispatchers.IO) {
            val url = buildUrl(path)
            val attempts = if (retrySafe && method == "GET") 2 else 1
            var lastError: Exception? = null

            repeat(attempts) { attempt ->
                try {
                    val requestBuilder = HttpRequest.newBuilder()
                        .uri(URI.create(url))
                        .timeout(endpoints.defaultTimeout)
                        .header("Accept", "application/json")
                        .header("Authorization", "Bearer $token")

                    val request = if (payload != null) {
                        requestBuilder
                            .header("Content-Type", "application/json")
                            .method(method, HttpRequest.BodyPublishers.ofString(payload))
                            .build()
                    } else {
                        requestBuilder
                            .method(method, HttpRequest.BodyPublishers.noBody())
                            .build()
                    }

                    val response = httpClient.send(request, HttpResponse.BodyHandlers.ofString())
                    val status = response.statusCode()
                    val body = response.body().orEmpty()

                    if (status in 200..299) {
                        return@withContext if (body.isBlank()) mapper.createObjectNode() else mapper.readTree(body)
                    }

                    if (retrySafe && method == "GET" && status >= 500 && attempt + 1 < attempts) {
                        logger.warn("Retrying GET $path due to server status $status")
                        return@repeat
                    }

                    throw toApiException(status, body)
                } catch (apiException: ApiException) {
                    throw apiException
                } catch (ex: Exception) {
                    lastError = ex
                    if (retrySafe && method == "GET" && attempt + 1 < attempts) {
                        logger.warn("Retrying GET $path due to network issue: ${ex.message}")
                        return@repeat
                    }
                    throw NetworkException("Network request failed: $method $path", ex)
                }
            }

            throw NetworkException("Network request failed: $method $path", lastError)
        }
    }

    private fun toApiException(status: Int, body: String): ApiException {
        val message = parseErrorMessage(body)
        return when (status) {
            401 -> UnauthorizedException(message)
            403 -> ForbiddenException(message)
            404 -> NotFoundException(message)
            409 -> ConflictException(message)
            429 -> RateLimitedException(message)
            in 500..599 -> ServerErrorException(status, message)
            else -> ApiException(status, message)
        }
    }

    private fun parseErrorMessage(body: String): String {
        if (body.isBlank()) return "Unexpected API error"
        return runCatching {
            val json = mapper.readTree(body)
            json.path("error").asText().ifBlank { json.path("message").asText() }
        }.getOrDefault(body)
    }

    private fun buildUrl(path: String): String {
        return baseUrl.trimEnd('/') + if (path.startsWith('/')) path else "/$path"
    }

    private fun endpoint(template: String, vararg params: Pair<String, String>): String {
        var result = template
        params.forEach { (key, value) ->
            result = result.replace("{$key}", value)
        }
        return result
    }

    private fun parseInstant(value: String?): Instant? {
        if (value.isNullOrBlank()) return null
        return runCatching { Instant.parse(value) }.getOrNull()
    }

    private fun mapSubmissionStatus(rawStatus: String): SubmissionStatus {
        return when (rawStatus.lowercase()) {
            "queued" -> SubmissionStatus.QUEUED
            "running", "processing" -> SubmissionStatus.RUNNING
            "accepted", "passed", "solved" -> SubmissionStatus.PASSED
            "wrong_answer", "failed", "rejected" -> SubmissionStatus.FAILED
            "compile_error", "runtime_error", "error" -> SubmissionStatus.ERROR
            "time_limit", "timeout" -> SubmissionStatus.TIMEOUT
            else -> SubmissionStatus.ERROR
        }
    }
}
