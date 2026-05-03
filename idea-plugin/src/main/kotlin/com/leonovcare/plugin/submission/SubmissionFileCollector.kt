package com.leonovcare.plugin.submission

import com.leonovcare.plugin.api.SubmissionFile
import java.nio.file.Files
import java.nio.file.Path

class SubmissionFileCollector {

    private val excludedDirectories = setOf(
        ".idea",
        ".gradle",
        "build",
        "target",
        "out",
        "node_modules",
    )

    private val excludedFileExtensions = setOf(".class", ".jar", ".iml", ".log")
    private val excludedFileNames = setOf(".platform-task.json")

    fun collect(taskRoot: Path): List<SubmissionFile> {
        if (!Files.exists(taskRoot)) return emptyList()

        return Files.walk(taskRoot).use { stream ->
            stream
                .filter { Files.isRegularFile(it) }
                .filter { isAllowed(taskRoot, it) }
                .map { file ->
                    val relative = taskRoot.relativize(file).toString().replace('\\', '/')
                    SubmissionFile(
                        path = relative,
                        content = Files.readString(file),
                    )
                }
                .toList()
        }
    }

    private fun isAllowed(taskRoot: Path, file: Path): Boolean {
        val relative = taskRoot.relativize(file).toString().replace('\\', '/')
        val segments = relative.split('/').filter { it.isNotBlank() }
        if (segments.any { excludedDirectories.contains(it) }) return false

        val fileName = file.fileName.toString()
        if (excludedFileNames.contains(fileName)) return false
        if (fileName.endsWith("~")) return false
        if (excludedFileExtensions.any { fileName.endsWith(it) }) return false

        return true
    }
}
