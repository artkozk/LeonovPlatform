package com.leonovcare.plugin.sync

import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.task.TaskStatus
import com.leonovcare.plugin.task.TaskType
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class SyncStatusMergerTest {

    @Test
    fun `keeps local status when remote is unknown`() {
        val existing = listOf(task("t1", TaskStatus.SOLVED))
        val remote = listOf(task("t1", TaskStatus.UNKNOWN))

        val result = SyncStatusMerger.merge(existing, remote)

        assertEquals(TaskStatus.SOLVED, result.tasks.first().status)
    }

    @Test
    fun `applies remote status when present`() {
        val existing = listOf(task("t1", TaskStatus.NEW))
        val remote = listOf(task("t1", TaskStatus.SOLVED))

        val result = SyncStatusMerger.merge(existing, remote)

        assertEquals(TaskStatus.SOLVED, result.tasks.first().status)
        assertEquals(1, result.changedStatuses)
    }

    private fun task(id: String, status: TaskStatus): Task {
        return Task(
            id = id,
            courseId = "c1",
            title = "Task $id",
            order = 1,
            status = status,
            type = TaskType.CONSOLE,
            language = "JAVA",
        )
    }
}
