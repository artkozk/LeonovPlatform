package com.leonovcare.plugin.settings

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage
import com.intellij.util.xmlb.XmlSerializerUtil
import com.leonovcare.plugin.util.PlatformConstants

@Service(Service.Level.APP)
@State(name = "LeonovCarePlatformSettings", storages = [Storage("leonovcare-platform-plugin.xml")])
class PlatformSettings : PersistentStateComponent<PlatformSettings.State> {

    data class State(
        var apiBaseUrl: String = PlatformConstants.DEFAULT_API_BASE_URL,
        var selectedCourseId: String? = null,
        var currentTaskId: String? = null,
        var uiMode: UIMode = UIMode.BEGINNER,
        var locale: String = "ru",
        var autoSyncEnabled: Boolean = true,
        var autoSyncIntervalMinutes: Int = 5,
        var closeFilesOnTaskSwitch: Boolean = false,
        var showSolvedTasks: Boolean = true,
        var enableLocalStyleAnalysis: Boolean = true,
        var enableServerStyleAnalysis: Boolean = true,
        var mockModeEnabled: Boolean = false,
        var restoreMissingTemplateFiles: Boolean = true,
        var authUserEmail: String? = null,
        var lastSyncEpochMillis: Long = 0L,
        var tasksCacheJson: String = "",
        var coursesCacheJson: String = "",
    )

    private var state: State = State()

    override fun getState(): State = state

    override fun loadState(state: State) {
        XmlSerializerUtil.copyBean(state, this.state)
    }

    fun mutableState(): State = state

    fun clearLocalCache() {
        state.tasksCacheJson = ""
        state.coursesCacheJson = ""
        state.currentTaskId = null
        state.lastSyncEpochMillis = 0L
    }

    companion object {
        fun getInstance(): PlatformSettings = ApplicationManager.getApplication().getService(PlatformSettings::class.java)
    }
}
