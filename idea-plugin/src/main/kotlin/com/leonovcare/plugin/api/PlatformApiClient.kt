package com.leonovcare.plugin.api

interface PlatformApiClient {
    suspend fun getCurrentUser(token: String): UserProfile
    suspend fun getCourses(token: String): List<Course>
    suspend fun getCourseTasks(token: String, courseId: String): List<Task>
    suspend fun getTaskDetails(token: String, taskId: String): TaskDetails
    suspend fun getTaskTemplate(token: String, taskId: String): TaskTemplate
    suspend fun submitSolution(token: String, taskId: String, request: SubmissionRequest): SubmissionResult
    suspend fun getSubmissionResult(token: String, taskId: String, attemptId: String): SubmissionResult
    suspend fun analyzeStyle(token: String, taskId: String, request: SubmissionRequest): CodeStyleResult?
    suspend fun getReferenceSolution(token: String, taskId: String): ReferenceSolution
    suspend fun requestAiHint(token: String, taskId: String, sourceCode: String): AiHintResponse?
    suspend fun resetProgress(token: String, taskId: String): Boolean
    suspend fun sync(token: String): SyncResult
    suspend fun markTaskInProgress(token: String, taskId: String): Boolean
}
