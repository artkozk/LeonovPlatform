package com.leonovcare.plugin.task

enum class TaskType {
    CONSOLE,
    UNIT_TEST,
    PROJECT,
    GAME,
    UNKNOWN;

    companion object {
        fun fromApi(value: String?): TaskType {
            return when (value?.trim()?.uppercase()) {
                "CONSOLE" -> CONSOLE
                "UNIT_TEST", "TEST", "UNITTEST" -> UNIT_TEST
                "PROJECT" -> PROJECT
                "GAME" -> GAME
                null, "" -> UNKNOWN
                else -> UNKNOWN
            }
        }
    }
}
