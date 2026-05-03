package com.leonovcare.plugin.run

import com.intellij.execution.RunnerAndConfigurationSettings
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.task.CurrentTaskContext

interface LanguageRunConfigurationProvider {
    fun supports(language: String): Boolean
    fun ensureConfiguration(project: Project, context: CurrentTaskContext): RunnerAndConfigurationSettings
}
