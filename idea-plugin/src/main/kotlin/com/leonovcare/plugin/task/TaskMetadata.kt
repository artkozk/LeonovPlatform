package com.leonovcare.plugin.task

import java.time.Instant

data class TaskMetadata(
    val taskId: String,
    val courseId: String,
    val language: String,
    val status: TaskStatus,
    val templateVersion: String,
    val openedAt: Instant,
    val lastSyncedAt: Instant,
    val filesMapping: Map<String, String>
)
