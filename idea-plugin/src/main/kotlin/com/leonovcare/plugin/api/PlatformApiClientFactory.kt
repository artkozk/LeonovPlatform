package com.leonovcare.plugin.api

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.leonovcare.plugin.settings.PlatformSettings

@Service(Service.Level.APP)
class PlatformApiClientFactory {

    private val settings = PlatformSettings.getInstance()
    @Volatile
    private var cachedBaseUrl: String? = null
    @Volatile
    private var cachedHttpClient: HttpPlatformApiClient? = null

    @Synchronized
    fun client(): PlatformApiClient {
        val state = settings.mutableState()
        return if (state.mockModeEnabled) {
            MockPlatformApiClient()
        } else {
            val baseUrl = state.apiBaseUrl.trim()
            val existing = cachedHttpClient
            if (existing != null && cachedBaseUrl == baseUrl) {
                existing
            } else {
                HttpPlatformApiClient(baseUrl).also {
                    cachedBaseUrl = baseUrl
                    cachedHttpClient = it
                }
            }
        }
    }

    companion object {
        fun getInstance(): PlatformApiClientFactory =
            ApplicationManager.getApplication().getService(PlatformApiClientFactory::class.java)
    }
}
