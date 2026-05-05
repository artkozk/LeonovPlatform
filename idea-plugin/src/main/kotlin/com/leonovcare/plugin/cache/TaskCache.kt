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
    private val cacheFileName = "tasks-by-course.json"

    fun getTasksByCourse(): Map<String, List<Task>> {
        val fileJson = PluginCacheStorage.readJson(cacheFileName)
        if (!fileJson.isNullOrBlank()) {
            return runCatching { mapper.readValue<Map<String, List<Task>>>(fileJson) }.getOrDefault(emptyMap())
        }

        val legacyJson = settings.mutableState().tasksCacheJson
        if (legacyJson.isBlank()) return emptyMap()

        val parsed = runCatching { mapper.readValue<Map<String, List<Task>>>(legacyJson) }.getOrDefault(emptyMap())
        if (parsed.isNotEmpty() && PluginCacheStorage.writeJson(cacheFileName, legacyJson)) {
            settings.mutableState().tasksCacheJson = ""
        }
        return parsed
    }

    fun saveTasksByCourse(tasksByCourse: Map<String, List<Task>>) {
        val json = mapper.writeValueAsString(tasksByCourse)
        if (PluginCacheStorage.writeJson(cacheFileName, json)) {
            settings.mutableState().tasksCacheJson = ""
        } else {
            settings.mutableState().tasksCacheJson = json
        }
    }

    fun clear() {
        PluginCacheStorage.delete(cacheFileName)
        settings.mutableState().tasksCacheJson = ""
    }

    companion object {
        fun getInstance(): TaskCache = ApplicationManager.getApplication().getService(TaskCache::class.java)
    }
}
