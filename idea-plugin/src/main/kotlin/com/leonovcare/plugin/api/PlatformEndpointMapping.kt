package com.leonovcare.plugin.api

import java.time.Duration

data class PlatformEndpointMapping(
    val me: String = "/me",
    val courses: String = "/courses",
    val courseDetails: String = "/courses/{courseId}",
    val courseTasksCatalog: String = "/courses/{courseId}/tasks-catalog",
    val lessonDetails: String = "/lessons/{lessonId}",
    val taskDetails: String = "/tasks/{taskId}",
    val taskTemplate: String = "/tasks/{taskId}/template",
    val taskSubmission: String = "/tasks/{taskId}/submissions",
    val submissionStatus: String = "/submissions/{submissionId}",
    val taskStyleCheck: String = "/tasks/{taskId}/style-check",
    val taskReferenceSolution: String = "/tasks/{taskId}/reference-solution",
    val aiTaskHint: String = "/ai/task-hint",
    val taskProgressReset: String = "/tasks/{taskId}/progress/reset",
    val taskProgressInProgress: String = "/tasks/{taskId}/progress/in-progress",
    val sync: String = "/sync",
    val defaultTimeout: Duration = Duration.ofSeconds(20),
)
