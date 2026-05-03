package com.leonovcare.plugin.settings

import com.intellij.openapi.options.SearchableConfigurable
import com.intellij.ui.components.JBCheckBox
import com.intellij.ui.components.JBTextField
import com.intellij.util.ui.FormBuilder
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.i18n.PlatformBundle
import javax.swing.JButton
import javax.swing.JComboBox
import javax.swing.JComponent
import javax.swing.JPanel

class PlatformSettingsConfigurable : SearchableConfigurable {

    private val settings = PlatformSettings.getInstance()

    private lateinit var panel: JPanel
    private lateinit var apiBaseUrlField: JBTextField
    private lateinit var uiModeCombo: JComboBox<UIMode>
    private lateinit var localeField: JBTextField
    private lateinit var selectedCourseField: JBTextField
    private lateinit var autoSyncCheckbox: JBCheckBox
    private lateinit var autoSyncIntervalField: JBTextField
    private lateinit var closeFilesCheckbox: JBCheckBox
    private lateinit var showSolvedCheckbox: JBCheckBox
    private lateinit var localStyleCheckbox: JBCheckBox
    private lateinit var serverStyleCheckbox: JBCheckBox
    private lateinit var mockModeCheckbox: JBCheckBox

    override fun getId(): String = "com.leonovcare.plugin.settings"

    override fun getDisplayName(): String = PlatformBundle.message("settings.displayName")

    override fun createComponent(): JComponent {
        apiBaseUrlField = JBTextField()
        uiModeCombo = JComboBox(UIMode.entries.toTypedArray())
        localeField = JBTextField()
        selectedCourseField = JBTextField()
        autoSyncCheckbox = JBCheckBox()
        autoSyncIntervalField = JBTextField()
        closeFilesCheckbox = JBCheckBox()
        showSolvedCheckbox = JBCheckBox()
        localStyleCheckbox = JBCheckBox()
        serverStyleCheckbox = JBCheckBox()
        mockModeCheckbox = JBCheckBox("Mock mode")

        val clearCacheButton = JButton(PlatformBundle.message("settings.clearCache"))
        clearCacheButton.addActionListener {
            settings.clearLocalCache()
        }

        val logoutButton = JButton(PlatformBundle.message("settings.logout"))
        logoutButton.addActionListener {
            AuthService.getInstance().logout()
        }

        panel = FormBuilder.createFormBuilder()
            .addLabeledComponent(PlatformBundle.message("settings.apiBaseUrl"), apiBaseUrlField)
            .addLabeledComponent(PlatformBundle.message("settings.uiMode"), uiModeCombo)
            .addLabeledComponent(PlatformBundle.message("settings.locale"), localeField)
            .addLabeledComponent(PlatformBundle.message("settings.selectedCourse"), selectedCourseField)
            .addLabeledComponent(PlatformBundle.message("settings.autoSync"), autoSyncCheckbox)
            .addLabeledComponent(PlatformBundle.message("settings.autoSyncInterval"), autoSyncIntervalField)
            .addLabeledComponent(PlatformBundle.message("settings.closeFilesOnSwitch"), closeFilesCheckbox)
            .addLabeledComponent(PlatformBundle.message("settings.showSolved"), showSolvedCheckbox)
            .addLabeledComponent(PlatformBundle.message("settings.enableLocalStyle"), localStyleCheckbox)
            .addLabeledComponent(PlatformBundle.message("settings.enableServerStyle"), serverStyleCheckbox)
            .addComponent(mockModeCheckbox)
            .addComponent(clearCacheButton)
            .addComponent(logoutButton)
            .addComponentFillVertically(JPanel(), 0)
            .panel

        reset()
        return panel
    }

    override fun isModified(): Boolean {
        val state = settings.mutableState()
        return apiBaseUrlField.text != state.apiBaseUrl ||
            uiModeCombo.selectedItem != state.uiMode ||
            localeField.text != state.locale ||
            selectedCourseField.text != (state.selectedCourseId ?: "") ||
            autoSyncCheckbox.isSelected != state.autoSyncEnabled ||
            autoSyncIntervalField.text != state.autoSyncIntervalMinutes.toString() ||
            closeFilesCheckbox.isSelected != state.closeFilesOnTaskSwitch ||
            showSolvedCheckbox.isSelected != state.showSolvedTasks ||
            localStyleCheckbox.isSelected != state.enableLocalStyleAnalysis ||
            serverStyleCheckbox.isSelected != state.enableServerStyleAnalysis ||
            mockModeCheckbox.isSelected != state.mockModeEnabled
    }

    override fun apply() {
        val state = settings.mutableState()
        state.apiBaseUrl = apiBaseUrlField.text.trim()
        state.uiMode = (uiModeCombo.selectedItem as? UIMode) ?: UIMode.BEGINNER
        state.locale = localeField.text.trim().ifBlank { "ru" }
        state.selectedCourseId = selectedCourseField.text.trim().ifBlank { null }
        state.autoSyncEnabled = autoSyncCheckbox.isSelected
        state.autoSyncIntervalMinutes = autoSyncIntervalField.text.toIntOrNull()?.coerceIn(1, 120) ?: 5
        state.closeFilesOnTaskSwitch = closeFilesCheckbox.isSelected
        state.showSolvedTasks = showSolvedCheckbox.isSelected
        state.enableLocalStyleAnalysis = localStyleCheckbox.isSelected
        state.enableServerStyleAnalysis = serverStyleCheckbox.isSelected
        state.mockModeEnabled = mockModeCheckbox.isSelected
    }

    override fun reset() {
        val state = settings.mutableState()
        apiBaseUrlField.text = state.apiBaseUrl
        uiModeCombo.selectedItem = state.uiMode
        localeField.text = state.locale
        selectedCourseField.text = state.selectedCourseId.orEmpty()
        autoSyncCheckbox.isSelected = state.autoSyncEnabled
        autoSyncIntervalField.text = state.autoSyncIntervalMinutes.toString()
        closeFilesCheckbox.isSelected = state.closeFilesOnTaskSwitch
        showSolvedCheckbox.isSelected = state.showSolvedTasks
        localStyleCheckbox.isSelected = state.enableLocalStyleAnalysis
        serverStyleCheckbox.isSelected = state.enableServerStyleAnalysis
        mockModeCheckbox.isSelected = state.mockModeEnabled
    }
}
