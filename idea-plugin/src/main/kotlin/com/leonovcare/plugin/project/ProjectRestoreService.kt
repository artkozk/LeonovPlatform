package com.leonovcare.plugin.project

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.task.TaskFileService

@Service(Service.Level.PROJECT)
class ProjectRestoreService(private val project: Project) {

    data class RestoreResult(
        val restored: Boolean,
        val message: String,
    )

    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val fileService = TaskFileService()

    fun restoreCurrentTask(overwriteEditable: Boolean): RestoreResult {
        val current = currentTaskService.getCurrentTask()
            ?: return RestoreResult(restored = false, message = "No opened task")

        val result = fileService.createOrUpdateTaskFiles(
            project = project,
            courseId = current.courseId,
            details = current.details,
            template = current.template,
            overwriteExistingEditableFiles = overwriteEditable,
        )

        return RestoreResult(
            restored = true,
            message = "Restored ${result.createdFiles} files, skipped ${result.skippedFiles}",
        )
    }

    companion object {
        fun getInstance(project: Project): ProjectRestoreService = project.getService(ProjectRestoreService::class.java)
    }
}
