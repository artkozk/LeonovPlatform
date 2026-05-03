package com.leonovcare.plugin.settings

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class PlatformSettingsStateTest {

    @Test
    fun `state load persists values`() {
        val settings = PlatformSettings()
        val state = PlatformSettings.State(
            apiBaseUrl = "http://localhost:9999/api/v1",
            selectedCourseId = "course-1",
            currentTaskId = "task-2",
            autoSyncIntervalMinutes = 15,
            closeFilesOnTaskSwitch = true,
        )

        settings.loadState(state)

        assertEquals("http://localhost:9999/api/v1", settings.state.apiBaseUrl)
        assertEquals("course-1", settings.state.selectedCourseId)
        assertEquals("task-2", settings.state.currentTaskId)
        assertEquals(15, settings.state.autoSyncIntervalMinutes)
        assertEquals(true, settings.state.closeFilesOnTaskSwitch)
    }
}
