package com.leonovcare.plugin.task

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class TaskStatusMappingTest {

    @Test
    fun `maps known statuses`() {
        assertEquals(TaskStatus.NEW, TaskStatus.fromApi("NEW"))
        assertEquals(TaskStatus.IN_PROGRESS, TaskStatus.fromApi("in_progress"))
        assertEquals(TaskStatus.SOLVED, TaskStatus.fromApi("ACCEPTED"))
        assertEquals(TaskStatus.FAILED, TaskStatus.fromApi("wrong_answer"))
    }

    @Test
    fun `maps locked and unavailable explicitly`() {
        assertEquals(TaskStatus.LOCKED, TaskStatus.fromApi("NEW", locked = true))
        assertEquals(TaskStatus.UNAVAILABLE, TaskStatus.fromApi("NEW", unavailable = true))
    }

    @Test
    fun `maps unknown status to UNKNOWN`() {
        assertEquals(TaskStatus.UNKNOWN, TaskStatus.fromApi("SOME_NEW_STATUS"))
        assertEquals(TaskStatus.UNKNOWN, TaskStatus.fromApi(null))
    }
}
