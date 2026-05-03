package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.StatementFormat
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.api.TaskStatement
import com.leonovcare.plugin.api.TaskTemplate
import com.leonovcare.plugin.api.TaskTemplateFile
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.nio.file.Files

class TaskFileServiceTest {

    @Test
    fun `creates template files and metadata`() {
        val root = Files.createTempDirectory("task-files-test")
        val service = TaskFileService()
        val details = sampleTaskDetails()
        val template = sampleTemplate()

        val result = service.createOrUpdateTaskFiles(
            projectRoot = root,
            courseId = "course-1",
            details = details,
            template = template,
            overwriteExistingEditableFiles = false,
        )

        assertTrue(Files.exists(result.mainFile))
        assertTrue(Files.exists(result.metadataFile))
        assertTrue(Files.exists(result.taskDirectory.resolve("statement.md")))
    }

    @Test
    fun `does not overwrite edited file when overwrite disabled`() {
        val root = Files.createTempDirectory("task-files-test")
        val service = TaskFileService()
        val details = sampleTaskDetails()
        val template = sampleTemplate()

        val first = service.createOrUpdateTaskFiles(root, "course-1", details, template, false)
        Files.writeString(first.mainFile, "// custom solution")

        service.createOrUpdateTaskFiles(root, "course-1", details, template, false)
        val content = Files.readString(first.mainFile)

        assertEquals("// custom solution", content)
    }

    @Test
    fun `protects against path traversal`() {
        val root = Files.createTempDirectory("task-files-test")
        val service = TaskFileService()
        val details = sampleTaskDetails()
        val template = TaskTemplate(
            taskId = "task-1",
            files = listOf(
                TaskTemplateFile("../outside.txt", "bad", editable = true)
            )
        )

        assertThrows(IllegalArgumentException::class.java) {
            service.createOrUpdateTaskFiles(root, "course-1", details, template, false)
        }
    }

    @Test
    fun `creates backup when overwrite enabled`() {
        val root = Files.createTempDirectory("task-files-test")
        val service = TaskFileService()
        val details = sampleTaskDetails()
        val template = sampleTemplate()

        val first = service.createOrUpdateTaskFiles(root, "course-1", details, template, false)
        Files.writeString(first.mainFile, "// edited")

        service.createOrUpdateTaskFiles(root, "course-1", details, template, true)

        val backupExists = Files.list(first.mainFile.parent)
            .use { stream -> stream.anyMatch { it.fileName.toString().contains(".bak-") } }
        assertTrue(backupExists)
        assertFalse(Files.readString(first.mainFile).contains("// edited"))
    }

    private fun sampleTaskDetails(): TaskDetails {
        return TaskDetails(
            id = "task-1",
            courseId = "course-1",
            title = "Hello",
            statement = TaskStatement(StatementFormat.MARKDOWN, "Body"),
            language = "JAVA",
            type = TaskType.CONSOLE,
            templateVersion = "1",
            entryPoint = "Solution",
            mainFilePath = "src/Solution.java",
        )
    }

    private fun sampleTemplate(): TaskTemplate {
        return TaskTemplate(
            taskId = "task-1",
            files = listOf(
                TaskTemplateFile(
                    path = "src/Solution.java",
                    content = "public class Solution {}",
                    editable = true,
                )
            )
        )
    }
}
