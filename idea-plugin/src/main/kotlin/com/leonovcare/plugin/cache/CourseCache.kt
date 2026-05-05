package com.leonovcare.plugin.cache

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.leonovcare.plugin.api.Course
import com.leonovcare.plugin.settings.PlatformSettings

@Service(Service.Level.APP)
class CourseCache {
    private val mapper = jacksonObjectMapper()
    private val settings = PlatformSettings.getInstance()
    private val cacheFileName = "courses.json"

    fun getCourses(): List<Course> {
        val fileJson = PluginCacheStorage.readJson(cacheFileName)
        if (!fileJson.isNullOrBlank()) {
            return runCatching { mapper.readValue<List<Course>>(fileJson) }.getOrDefault(emptyList())
        }

        val legacyJson = settings.mutableState().coursesCacheJson
        if (legacyJson.isBlank()) return emptyList()

        val parsed = runCatching { mapper.readValue<List<Course>>(legacyJson) }.getOrDefault(emptyList())
        if (parsed.isNotEmpty() && PluginCacheStorage.writeJson(cacheFileName, legacyJson)) {
            settings.mutableState().coursesCacheJson = ""
        }
        return parsed
    }

    fun saveCourses(courses: List<Course>) {
        val json = mapper.writeValueAsString(courses)
        if (PluginCacheStorage.writeJson(cacheFileName, json)) {
            settings.mutableState().coursesCacheJson = ""
        } else {
            settings.mutableState().coursesCacheJson = json
        }
    }

    companion object {
        fun getInstance(): CourseCache = ApplicationManager.getApplication().getService(CourseCache::class.java)
    }
}
