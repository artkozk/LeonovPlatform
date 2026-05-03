package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.api.TaskTemplate
import java.nio.file.Path

data class CurrentTaskContext(
    val courseId: String,
    val task: Task,
    val details: TaskDetails,
    val template: TaskTemplate,
    val taskDir: Path,
)
