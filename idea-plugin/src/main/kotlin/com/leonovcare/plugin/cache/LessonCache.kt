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
    private val cacheFileName = "lessons-by-id.json"

    fun getLessonsById(): Map<String, LessonMaterial> {
        val fileJson = PluginCacheStorage.readJson(cacheFileName)
        if (!fileJson.isNullOrBlank()) {
            return runCatching { mapper.readValue<Map<String, LessonMaterial>>(fileJson) }.getOrDefault(emptyMap())
        }

        val legacyJson = settings.mutableState().lessonsCacheJson
        if (legacyJson.isBlank()) return emptyMap()

        val parsed = runCatching { mapper.readValue<Map<String, LessonMaterial>>(legacyJson) }.getOrDefault(emptyMap())
        if (parsed.isNotEmpty() && PluginCacheStorage.writeJson(cacheFileName, legacyJson)) {
            settings.mutableState().lessonsCacheJson = ""
        }
        return parsed
    }

    fun saveLessonsById(lessonsById: Map<String, LessonMaterial>) {
        val json = mapper.writeValueAsString(lessonsById)
        if (PluginCacheStorage.writeJson(cacheFileName, json)) {
            settings.mutableState().lessonsCacheJson = ""
        } else {
            settings.mutableState().lessonsCacheJson = json
        }
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
        PluginCacheStorage.delete(cacheFileName)
        settings.mutableState().lessonsCacheJson = ""
    }

    companion object {
        fun getInstance(): LessonCache = ApplicationManager.getApplication().getService(LessonCache::class.java)
    }
}
