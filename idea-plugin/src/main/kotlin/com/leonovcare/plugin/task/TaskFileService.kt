package com.leonovcare.plugin.task

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.api.TaskTemplate
import com.leonovcare.plugin.api.TaskTemplateFile
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardCopyOption
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

class TaskFileService {

    private val logger = Logger.getInstance(TaskFileService::class.java)
    private val mapper = jacksonObjectMapper()

    data class Result(
        val taskDirectory: Path,
        val mainFile: Path,
        val metadataFile: Path,
        val createdFiles: Int,
        val skippedFiles: Int,
    )

    fun createOrUpdateTaskFiles(
        project: Project,
        courseId: String,
        details: TaskDetails,
        template: TaskTemplate,
        overwriteExistingEditableFiles: Boolean,
    ): Result {
        val projectBase = project.basePath ?: error("Project has no base path")
        val projectRoot = Path.of(projectBase)
        return createOrUpdateTaskFiles(
            projectRoot = projectRoot,
            courseId = courseId,
            details = details,
            template = template,
            overwriteExistingEditableFiles = overwriteExistingEditableFiles,
        )
    }

    fun createOrUpdateTaskFiles(
        projectRoot: Path,
        courseId: String,
        details: TaskDetails,
        template: TaskTemplate,
        overwriteExistingEditableFiles: Boolean,
    ): Result {
        val taskDir = projectRoot
            .resolve("platform-tasks")
            .resolve("course-$courseId")
            .resolve("task-${details.id}")
            .normalize()

        Files.createDirectories(taskDir)

        var created = 0
        var skipped = 0

        template.files.forEach { templateFile ->
            val resolved = resolveSafe(taskDir, templateFile.path)
            Files.createDirectories(resolved.parent)

            if (Files.exists(resolved) && templateFile.editable && !overwriteExistingEditableFiles) {
                skipped++
                return@forEach
            }

            if (Files.exists(resolved) && templateFile.editable && overwriteExistingEditableFiles) {
                createBackup(resolved)
            }

            Files.writeString(resolved, templateFile.content)
            created++
        }

        val statementPath = resolveSafe(taskDir, "statement.md")
        if (!Files.exists(statementPath)) {
            Files.writeString(statementPath, details.statement.body)
        }

        val metadataPath = resolveSafe(taskDir, ".platform-task.json")
        val metadata = mapOf(
            "taskId" to details.id,
            "courseId" to courseId,
            "language" to details.language,
            "status" to TaskStatus.IN_PROGRESS.name,
            "templateVersion" to details.templateVersion,
            "openedAt" to Instant.now().toString(),
            "lastSyncedAt" to Instant.now().toString(),
            "filesMapping" to template.files.associate { it.path to it.path },
        )
        Files.writeString(metadataPath, mapper.writerWithDefaultPrettyPrinter().writeValueAsString(metadata))

        val mainFile = resolveSafe(taskDir, details.mainFilePath)
        if (!Files.exists(mainFile)) {
            val fallback = template.files.firstOrNull() ?: TaskTemplateFile(details.mainFilePath, "", editable = true)
            val fallbackPath = resolveSafe(taskDir, fallback.path)
            if (Files.exists(fallbackPath)) {
                Files.copy(fallbackPath, mainFile, StandardCopyOption.REPLACE_EXISTING)
            } else {
                Files.createDirectories(mainFile.parent)
                Files.writeString(mainFile, fallback.content)
            }
        }

        logger.info("Task files prepared: taskId=${details.id}, created=$created, skipped=$skipped")
        return Result(taskDir, mainFile, metadataPath, created, skipped)
    }

    fun resolveSafe(root: Path, relativePath: String): Path {
        val normalized = root.resolve(relativePath).normalize()
        if (!normalized.startsWith(root)) {
            throw IllegalArgumentException("Path traversal detected: $relativePath")
        }
        return normalized
    }

    private fun createBackup(path: Path) {
        val stamp = DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss").withZone(ZoneOffset.UTC).format(Instant.now())
        val backup = path.resolveSibling("${path.fileName}.bak-$stamp")
        Files.copy(path, backup, StandardCopyOption.REPLACE_EXISTING)
    }
}
