package com.leonovcare.plugin.cache

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.settings.PlatformSettings

@Service(Service.Level.APP)
class LessonCache {
    private val mapper = jacksonObjectMapper()
    private val settings = PlatformSettings.getInstance()

    fun getLessonsById(): Map<String, LessonMaterial> {
        val json = settings.mutableState().lessonsCacheJson
        if (json.isBlank()) return emptyMap()
        return runCatching { mapper.readValue<Map<String, LessonMaterial>>(json) }.getOrDefault(emptyMap())
    }

    fun saveLessonsById(lessonsById: Map<String, LessonMaterial>) {
        settings.mutableState().lessonsCacheJson = mapper.writeValueAsString(lessonsById)
    }

    fun upsert(lesson: LessonMaterial) {
        val updated = getLessonsById().toMutableMap()
        updated[lesson.id] = lesson
        saveLessonsById(updated)
    }

    fun findByTaskId(taskId: String): LessonMaterial? {
        return getLessonsById().values.firstOrNull { lesson ->
            lesson.tasks.any { it.id == taskId } || lesson.blocks.any { it.taskId == taskId }
        }
    }

    fun clear() {
        settings.mutableState().lessonsCacheJson = ""
    }

    companion object {
        fun getInstance(): LessonCache = ApplicationManager.getApplication().getService(LessonCache::class.java)
    }
}
