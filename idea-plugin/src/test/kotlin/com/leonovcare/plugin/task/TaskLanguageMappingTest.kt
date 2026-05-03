package com.leonovcare.plugin.task

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class TaskLanguageMappingTest {

    @Test
    fun `maps known API values to canonical languages`() {
        assertEquals(TaskLanguage.JAVA, TaskLanguage.fromApi("java"))
        assertEquals(TaskLanguage.PYTHON, TaskLanguage.fromApi("python3"))
        assertEquals(TaskLanguage.KOTLIN, TaskLanguage.fromApi("kt"))
        assertEquals(TaskLanguage.SQL, TaskLanguage.fromApi("postgresql"))
        assertEquals(TaskLanguage.JAVASCRIPT, TaskLanguage.fromApi("js"))
    }

    @Test
    fun `maps unknown values to UNKNOWN`() {
        assertEquals(TaskLanguage.UNKNOWN, TaskLanguage.fromApi("go"))
        assertEquals(TaskLanguage.UNKNOWN, TaskLanguage.fromApi(null))
    }
}
