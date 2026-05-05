package com.leonovcare.plugin.util

import com.intellij.ide.plugins.PluginManagerCore
import com.intellij.openapi.application.ApplicationNamesInfo
import com.intellij.openapi.extensions.PluginId

object PluginRuntimeInfo {
    private const val PLUGIN_ID = "com.leonovcare.plugin"

    fun pluginVersion(): String {
        val id = PluginId.getId(PLUGIN_ID)
        return PluginManagerCore.getPlugin(id)?.version ?: "unknown"
    }

    fun idePlatformName(): String {
        return ApplicationNamesInfo.getInstance().fullProductName
    }
}
