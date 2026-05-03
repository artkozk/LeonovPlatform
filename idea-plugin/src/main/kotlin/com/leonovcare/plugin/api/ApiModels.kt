package com.leonovcare.plugin.api

import com.leonovcare.plugin.task.TaskStatus
import com.leonovcare.plugin.task.TaskType
import java.time.Instant

data class UserProfile(
    val id: String,
    val email: String,
    val displayName: String,
    val avatarUrl: String? = null,
)

data class Course(
    val id: String,
    val title: String,
    val description: String,
    val progressPercent: Int = 0,
    val tasksTotal: Int = 0,
    val tasksSolved: Int = 0,
)

data class CourseModule(
    val id: String,
    val title: String,
    val order: Int,
)

data class Task(
    val id: String,
    val courseId: String,
    val moduleId: String? = null,
    val lessonId: String? = null,
    val lessonTitle: String? = null,
    val title: String,
    val order: Int,
    val status: TaskStatus,
    val type: TaskType,
    val language: String,
    val locked: Boolean = false,
    val unavailable: Boolean = false,
)

enum class StatementFormat {
    MARKDOWN,
    HTML,
    TEXT,
}

data class TaskStatement(
    val format: StatementFormat,
    val body: String,
    val requirements: List<String> = emptyList(),
    val inputDescription: String = "",
    val outputDescription: String = "",
    val constraints: List<String> = emptyList(),
)

data class TaskDetails(
    val id: String,
    val courseId: String,
    val title: String,
    val statement: TaskStatement,
    val language: String,
    val type: TaskType,
    val templateVersion: String,
    val entryPoint: String,
    val mainFilePath: String,
)

data class LessonTaskSummary(
    val id: String,
    val title: String,
    val type: TaskType,
    val language: String,
)

data class LessonBlock(
    val id: String,
    val type: String,
    val title: String,
    val contentMd: String,
    val position: Int,
    val taskId: String? = null,
    val taskTitle: String? = null,
)

data class LessonMaterial(
    val id: String,
    val title: String,
    val moduleTitle: String,
    val position: Int,
    val contentMd: String,
    val tasks: List<LessonTaskSummary>,
    val blocks: List<LessonBlock>,
    val fetchedAtEpochMillis: Long = System.currentTimeMillis(),
)

data class TaskTemplateFile(
    val path: String,
    val content: String,
    val editable: Boolean,
)

data class TaskTemplate(
    val taskId: String,
    val files: List<TaskTemplateFile>,
)

data class TaskProgress(
    val taskId: String,
    val status: TaskStatus,
    val updatedAt: Instant,
)

data class SubmissionFile(
    val path: String,
    val content: String,
)

data class SubmissionClientInfo(
    val pluginVersion: String,
    val ideVersion: String,
    val platform: String,
)

data class SubmissionRequest(
    val taskId: String,
    val language: String,
    val files: List<SubmissionFile>,
    val client: SubmissionClientInfo,
    val projectId: String? = null,
    val courseId: String? = null,
    val localAttemptId: String? = null,
)

enum class SubmissionStatus {
    QUEUED,
    RUNNING,
    PASSED,
    FAILED,
    ERROR,
    TIMEOUT,
}

enum class TestResultStatus {
    PASSED,
    FAILED,
    SKIPPED,
    ERROR,
}

data class TestResult(
    val name: String,
    val status: TestResultStatus,
    val message: String = "",
    val expected: String? = null,
    val actual: String? = null,
    val input: String? = null,
    val output: String? = null,
    val errorOutput: String? = null,
    val durationMs: Long? = null,
)

enum class Severity {
    INFO,
    WARNING,
    ERROR,
}

data class CodeStyleItem(
    val severity: Severity,
    val filePath: String,
    val line: Int,
    val column: Int,
    val message: String,
    val ruleId: String = "",
    val quickFixAvailable: Boolean = false,
)

data class CodeStyleResult(
    val items: List<CodeStyleItem>,
)

data class SubmissionResult(
    val attemptId: String,
    val status: SubmissionStatus,
    val score: Int? = null,
    val maxScore: Int? = null,
    val message: String = "",
    val testResults: List<TestResult> = emptyList(),
    val styleResults: List<CodeStyleItem> = emptyList(),
    val executionTimeMs: Long? = null,
    val memoryUsedMb: Int? = null,
    val createdAt: Instant? = null,
    val completedAt: Instant? = null,
)

data class ReferenceSolutionFile(
    val path: String,
    val content: String,
)

data class ReferenceSolution(
    val taskId: String,
    val files: List<ReferenceSolutionFile>,
    val explanation: String? = null,
    val available: Boolean,
    val unavailableReason: String? = null,
)

data class SyncResult(
    val updatedTasks: Int,
    val changedStatuses: Int,
    val unlockedTasks: Int,
    val serverTime: Instant,
    val errors: List<String> = emptyList(),
)

data class AiHintUsage(
    val promptTokens: Int = 0,
    val completionTokens: Int = 0,
    val totalTokens: Int = 0,
)

data class AiHintResponse(
    val status: String,
    val hint: String,
    val model: String? = null,
    val usage: AiHintUsage? = null,
)
