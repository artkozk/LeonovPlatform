package com.leonovcare.plugin.api

import com.leonovcare.plugin.task.TaskStatus
import com.leonovcare.plugin.task.TaskType
import java.time.Instant

class MockPlatformApiClient : PlatformApiClient {

    private val mockTaskId = "task-1"

    override suspend fun getCurrentUser(token: String): UserProfile {
        if (token.isBlank()) throw UnauthorizedException("Token is empty")
        return UserProfile(
            id = "user-1",
            email = "student@example.com",
            displayName = "Student",
            avatarUrl = null,
        )
    }

    override suspend fun getCourses(token: String): List<Course> {
        return listOf(
            Course(
                id = "course-java",
                title = "Java Developer",
                description = "Mock course",
                progressPercent = 35,
                tasksTotal = 10,
                tasksSolved = 3,
            )
        )
    }

    override suspend fun getCourseTasks(token: String, courseId: String): List<Task> {
        return listOf(
            Task(
                id = mockTaskId,
                courseId = courseId,
                moduleId = "module-1",
                lessonId = "lesson-1",
                lessonTitle = "Первый урок",
                title = "Hello, World",
                order = 1,
                status = TaskStatus.NEW,
                type = TaskType.CONSOLE,
                language = "JAVA",
                locked = false,
            )
        )
    }

    override suspend fun getLessonMaterial(token: String, lessonId: String): LessonMaterial {
        return LessonMaterial(
            id = lessonId,
            title = "Первый урок",
            moduleTitle = "Введение",
            position = 1,
            contentMd = "Это mock-теория урока. Здесь будет объяснение темы.",
            tasks = listOf(
                LessonTaskSummary(
                    id = mockTaskId,
                    title = "Hello, World",
                    type = TaskType.CONSOLE,
                    language = "JAVA",
                ),
            ),
            blocks = listOf(
                LessonBlock(
                    id = "block-1",
                    type = "theory",
                    title = "Теория",
                    contentMd = "Текст теории для локального просмотра в IDE.",
                    position = 1,
                ),
                LessonBlock(
                    id = "block-2",
                    type = "practice",
                    title = "Практика",
                    contentMd = "Сделайте задачу Hello, World.",
                    position = 2,
                    taskId = mockTaskId,
                    taskTitle = "Hello, World",
                ),
            ),
        )
    }

    override suspend fun getTaskDetails(token: String, taskId: String): TaskDetails {
        return TaskDetails(
            id = mockTaskId,
            courseId = "course-java",
            title = "Hello, World",
            statement = TaskStatement(
                format = StatementFormat.MARKDOWN,
                body = "Write a program that prints Hello, World.",
                requirements = listOf("Print exactly: Hello, World"),
            ),
            language = "JAVA",
            type = TaskType.CONSOLE,
            templateVersion = "1",
            entryPoint = "Solution",
            mainFilePath = "src/Solution.java",
        )
    }

    override suspend fun getTaskTemplate(token: String, taskId: String): TaskTemplate {
        return TaskTemplate(
            taskId = taskId,
            files = listOf(
                TaskTemplateFile(
                    path = "src/Solution.java",
                    content = "public class Solution {\n    public static void main(String[] args) {\n        // write your code here\n    }\n}\n",
                    editable = true,
                )
            )
        )
    }

    override suspend fun submitSolution(token: String, taskId: String, request: SubmissionRequest): SubmissionResult {
        return SubmissionResult(
            attemptId = "attempt-mock-1",
            status = SubmissionStatus.PASSED,
            score = 100,
            maxScore = 100,
            message = "All tests passed",
            testResults = listOf(
                TestResult(
                    name = "Test 1",
                    status = TestResultStatus.PASSED,
                    expected = "Hello, World",
                    actual = "Hello, World",
                    durationMs = 10,
                )
            ),
            executionTimeMs = 100,
            memoryUsedMb = 16,
            createdAt = Instant.now(),
            completedAt = Instant.now(),
        )
    }

    override suspend fun getSubmissionResult(token: String, taskId: String, attemptId: String): SubmissionResult {
        return submitSolution(token, taskId, SubmissionRequest(taskId, "JAVA", emptyList(), SubmissionClientInfo("0", "0", "IDEA")))
    }

    override suspend fun analyzeStyle(token: String, taskId: String, request: SubmissionRequest): CodeStyleResult {
        return CodeStyleResult(
            items = listOf(
                CodeStyleItem(
                    severity = Severity.WARNING,
                    filePath = "src/Solution.java",
                    line = 1,
                    column = 1,
                    message = "Mock style warning",
                    ruleId = "mock-warning",
                    quickFixAvailable = false,
                )
            )
        )
    }

    override suspend fun getReferenceSolution(token: String, taskId: String): ReferenceSolution {
        return ReferenceSolution(
            taskId = taskId,
            files = listOf(
                ReferenceSolutionFile(
                    path = "src/Solution.java",
                    content = "public class Solution {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World\");\n    }\n}\n",
                )
            ),
            explanation = "The program prints the required string.",
            available = true,
        )
    }

    override suspend fun requestAiHint(token: String, taskId: String, sourceCode: String): AiHintResponse {
        return AiHintResponse(
            status = "ok",
            hint = "Начните с декомпозиции задачи на 2-3 шага и проверьте ввод/вывод на простом примере.",
            model = "mock-local",
            usage = AiHintUsage(promptTokens = 0, completionTokens = 0, totalTokens = 0),
        )
    }

    override suspend fun resetProgress(token: String, taskId: String): Boolean = true

    override suspend fun sync(token: String): SyncResult {
        return SyncResult(
            updatedTasks = 1,
            changedStatuses = 0,
            unlockedTasks = 0,
            serverTime = Instant.now(),
        )
    }

    override suspend fun markTaskInProgress(token: String, taskId: String): Boolean = true
}
