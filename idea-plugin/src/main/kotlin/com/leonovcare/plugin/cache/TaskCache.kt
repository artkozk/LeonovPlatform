package com.leonovcare.plugin.cache

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.settings.PlatformSettings

@Service(Service.Level.APP)
class TaskCache {
    private val mapper = jacksonObjectMapper()
    private val settings = PlatformSettings.getInstance()

    fun getTasksByCourse(): Map<String, List<Task>> {
        val json = settings.mutableState().tasksCacheJson
        if (json.isBlank()) return emptyMap()
        return runCatching { mapper.readValue<Map<String, List<Task>>>(json) }.getOrDefault(emptyMap())
    }

    fun saveTasksByCourse(tasksByCourse: Map<String, List<Task>>) {
        settings.mutableState().tasksCacheJson = mapper.writeValueAsString(tasksByCourse)
    }

    fun clear() {
        settings.mutableState().tasksCacheJson = ""
    }

    companion object {
        fun getInstance(): TaskCache = ApplicationManager.getApplication().getService(TaskCache::class.java)
    }
}
