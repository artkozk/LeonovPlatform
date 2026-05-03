package com.leonovcare.plugin.task

enum class TaskStatus {
    NEW,
    IN_PROGRESS,
    SOLVED,
    FAILED,
    LOCKED,
    UNAVAILABLE,
    UNKNOWN;

    companion object {
        fun fromApi(value: String?, locked: Boolean = false, unavailable: Boolean = false): TaskStatus {
            if (locked) return LOCKED
            if (unavailable) return UNAVAILABLE
            return when (value?.trim()?.uppercase()) {
                "NEW" -> NEW
                "IN_PROGRESS", "INPROGRESS", "STARTED" -> IN_PROGRESS
                "SOLVED", "ACCEPTED", "PASSED" -> SOLVED
                "FAILED", "WRONG_ANSWER", "REJECTED" -> FAILED
                "LOCKED" -> LOCKED
                "UNAVAILABLE", "HIDDEN" -> UNAVAILABLE
                null, "" -> UNKNOWN
                else -> UNKNOWN
            }
        }
    }
}
