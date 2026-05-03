package com.leonovcare.plugin.actions

import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.project.DumbAwareAction
import com.intellij.openapi.options.ShowSettingsUtil
import com.leonovcare.plugin.settings.PlatformSettingsConfigurable

class OpenPluginSettingsAction : DumbAwareAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project
        ShowSettingsUtil.getInstance().showSettingsDialog(project, PlatformSettingsConfigurable::class.java)
    }
}

