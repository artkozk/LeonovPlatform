package com.leonovcare.plugin.run

import com.intellij.execution.RunnerAndConfigurationSettings
import com.intellij.execution.ProgramRunnerUtil
import com.intellij.execution.executors.DefaultDebugExecutor
import com.intellij.execution.executors.DefaultRunExecutor
import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.CurrentTaskContext
import com.leonovcare.plugin.task.TaskLanguage
import com.leonovcare.plugin.task.CurrentTaskService

class UnsupportedLanguageRunConfigurationProvider : LanguageRunConfigurationProvider {
    override fun supports(language: String): Boolean = true

    override fun ensureConfiguration(project: Project, context: CurrentTaskContext): RunnerAndConfigurationSettings {
        val language = TaskLanguage.fromApi(context.details.language)
        throw IllegalStateException(
            PlatformBundle.message("errors.unsupportedLanguageWithName", language.apiName),
        )
    }
}

@Service(Service.Level.PROJECT)
class TaskRunConfigurationService(private val project: Project) {

    private val providers: List<LanguageRunConfigurationProvider> = buildList {
        add(UnsupportedLanguageRunConfigurationProvider())
    }

    fun runCurrentTask(debug: Boolean = false) {
        val context = CurrentTaskService.getInstance(project).getCurrentTask()
            ?: throw IllegalStateException(PlatformBundle.message("errors.taskUnavailable"))

        val provider = providers.firstOrNull { it.supports(context.details.language) }
            ?: throw IllegalStateException(PlatformBundle.message("errors.unsupportedLanguageWithName", context.details.language))

        val settings = provider.ensureConfiguration(project, context)
        val executor = if (debug) DefaultDebugExecutor.getDebugExecutorInstance() else DefaultRunExecutor.getRunExecutorInstance()
        ProgramRunnerUtil.executeConfiguration(settings, executor)
    }

    companion object {
        fun getInstance(project: Project): TaskRunConfigurationService = project.getService(TaskRunConfigurationService::class.java)
    }
}
