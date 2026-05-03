package com.leonovcare.plugin.api

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.leonovcare.plugin.settings.PlatformSettings

@Service(Service.Level.APP)
class PlatformApiClientFactory {

    private val settings = PlatformSettings.getInstance()

    fun client(): PlatformApiClient {
        val state = settings.mutableState()
        return if (state.mockModeEnabled) {
            MockPlatformApiClient()
        } else {
            HttpPlatformApiClient(state.apiBaseUrl)
        }
    }

    companion object {
        fun getInstance(): PlatformApiClientFactory =
            ApplicationManager.getApplication().getService(PlatformApiClientFactory::class.java)
    }
}
