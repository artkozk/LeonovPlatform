package com.leonovcare.plugin.task

enum class TaskLanguage(
    val apiName: String,
    val defaultMainFilePath: String,
    val defaultEntryPoint: String,
) {
    JAVA(
        apiName = "JAVA",
        defaultMainFilePath = "src/Solution.java",
        defaultEntryPoint = "Solution",
    ),
    KOTLIN(
        apiName = "KOTLIN",
        defaultMainFilePath = "src/main/kotlin/Main.kt",
        defaultEntryPoint = "MainKt",
    ),
    PYTHON(
        apiName = "PYTHON",
        defaultMainFilePath = "src/main/python/solution.py",
        defaultEntryPoint = "main.py",
    ),
    SQL(
        apiName = "SQL",
        defaultMainFilePath = "src/main/sql/query.sql",
        defaultEntryPoint = "query.sql",
    ),
    JAVASCRIPT(
        apiName = "JAVASCRIPT",
        defaultMainFilePath = "src/main/js/solution.js",
        defaultEntryPoint = "solution.js",
    ),
    UNKNOWN(
        apiName = "UNKNOWN",
        defaultMainFilePath = "src/Solution.java",
        defaultEntryPoint = "Solution",
    );

    companion object {
        fun fromApi(value: String?): TaskLanguage {
            val normalized = value?.trim()?.uppercase().orEmpty()
            return when (normalized) {
                "JAVA" -> JAVA
                "KOTLIN", "KT" -> KOTLIN
                "PYTHON", "PY", "PYTHON3" -> PYTHON
                "SQL", "POSTGRESQL", "MYSQL" -> SQL
                "JAVASCRIPT", "JS", "NODE" -> JAVASCRIPT
                else -> UNKNOWN
            }
        }
    }
}
