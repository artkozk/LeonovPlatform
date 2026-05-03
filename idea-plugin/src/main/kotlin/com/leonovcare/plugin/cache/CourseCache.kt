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

    fun getCourses(): List<Course> {
        val json = settings.mutableState().coursesCacheJson
        if (json.isBlank()) return emptyList()
        return runCatching { mapper.readValue<List<Course>>(json) }.getOrDefault(emptyList())
    }

    fun saveCourses(courses: List<Course>) {
        settings.mutableState().coursesCacheJson = mapper.writeValueAsString(courses)
    }

    companion object {
        fun getInstance(): CourseCache = ApplicationManager.getApplication().getService(CourseCache::class.java)
    }
}
