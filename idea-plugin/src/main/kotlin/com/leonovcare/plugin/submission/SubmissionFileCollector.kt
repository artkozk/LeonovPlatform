package com.leonovcare.plugin.submission

import com.leonovcare.plugin.api.SubmissionFile
import com.leonovcare.plugin.i18n.PlatformBundle
import java.nio.file.Files
import java.nio.file.Path
import kotlin.math.max

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
    private val maxFilesPerSubmission = 250
    private val maxTotalBytesPerSubmission = 16L * 1024L * 1024L
    private val maxSingleFileBytes = 8L * 1024L * 1024L

    fun collect(taskRoot: Path): List<SubmissionFile> {
        if (!Files.exists(taskRoot)) return emptyList()

        val files = Files.walk(taskRoot).use { stream ->
            stream
                .filter { Files.isRegularFile(it) }
                .filter { isAllowed(taskRoot, it) }
                .sorted()
                .toList()
        }

        if (files.size > maxFilesPerSubmission) {
            throw IllegalStateException(
                PlatformBundle.message("errors.submissionTooManyFiles", files.size, maxFilesPerSubmission),
            )
        }

        var totalBytes = 0L
        val result = ArrayList<SubmissionFile>(max(files.size, 1))
        for (file in files) {
            val fileSize = runCatching { Files.size(file) }.getOrDefault(0L)
            if (fileSize > maxSingleFileBytes) {
                val relative = taskRoot.relativize(file).toString().replace('\\', '/')
                throw IllegalStateException(
                    PlatformBundle.message(
                        "errors.submissionFileTooLarge",
                        relative,
                        fileSize,
                        maxSingleFileBytes,
                    ),
                )
            }

            totalBytes += fileSize
            if (totalBytes > maxTotalBytesPerSubmission) {
                throw IllegalStateException(
                    PlatformBundle.message(
                        "errors.submissionPayloadTooLarge",
                        totalBytes,
                        maxTotalBytesPerSubmission,
                    ),
                )
            }

            result += SubmissionFile(
                path = taskRoot.relativize(file).toString().replace('\\', '/'),
                content = Files.readString(file),
            )
        }

        return result
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
