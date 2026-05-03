package com.leonovcare.plugin.submission

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.nio.file.Files

class SubmissionFileCollectorTest {

    @Test
    fun `collect excludes ide and build artifacts`() {
        val root = Files.createTempDirectory("submission-files-test")

        Files.createDirectories(root.resolve("src"))
        Files.createDirectories(root.resolve(".idea"))
        Files.createDirectories(root.resolve("build"))
        Files.createDirectories(root.resolve("target"))
        Files.createDirectories(root.resolve("out"))
        Files.createDirectories(root.resolve(".gradle"))

        Files.writeString(root.resolve("src/Solution.java"), "class Solution {}")
        Files.writeString(root.resolve(".idea/workspace.xml"), "skip")
        Files.writeString(root.resolve("build/tmp.txt"), "skip")
        Files.writeString(root.resolve("target/result.txt"), "skip")
        Files.writeString(root.resolve("out/App.class"), "skip")
        Files.writeString(root.resolve(".platform-task.json"), "skip")

        val files = SubmissionFileCollector().collect(root)

        assertEquals(1, files.size)
        assertEquals("src/Solution.java", files.first().path)
        assertTrue(files.first().content.contains("Solution"))
    }
}
