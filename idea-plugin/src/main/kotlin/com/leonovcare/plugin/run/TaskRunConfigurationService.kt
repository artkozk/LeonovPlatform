package com.leonovcare.plugin.run

import com.intellij.execution.RunnerAndConfigurationSettings
import com.intellij.execution.ProgramRunnerUtil
import com.intellij.execution.application.ApplicationConfiguration
import com.intellij.execution.application.ApplicationConfigurationType
import com.intellij.execution.executors.DefaultDebugExecutor
import com.intellij.execution.executors.DefaultRunExecutor
import com.intellij.openapi.components.Service
import com.intellij.openapi.module.ModuleManager
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.CurrentTaskContext
import com.leonovcare.plugin.task.TaskLanguage
import com.leonovcare.plugin.task.CurrentTaskService
import java.nio.file.Files

class JavaRunConfigurationProvider : LanguageRunConfigurationProvider {

    override fun supports(language: String): Boolean {
        return TaskLanguage.fromApi(language) == TaskLanguage.JAVA
    }

    override fun ensureConfiguration(project: Project, context: CurrentTaskContext): RunnerAndConfigurationSettings {
        val runManager = com.intellij.execution.RunManager.getInstance(project)
        val configType = ApplicationConfigurationType.getInstance()
        val configName = "Task ${context.task.id}"

        val existing = runManager.allSettings.firstOrNull { it.name == configName }
        val settings = existing ?: runManager.createConfiguration(configName, configType.configurationFactories[0])
        val runConfiguration = settings.configuration as ApplicationConfiguration

        runConfiguration.mainClassName = detectMainClass(context)
        runConfiguration.workingDirectory = context.taskDir.toString()
        runConfiguration.setModule(ModuleManager.getInstance(project).modules.firstOrNull())

        if (existing == null) {
            runManager.addConfiguration(settings)
        }
        return settings
    }

    private fun detectMainClass(context: CurrentTaskContext): String {
        if (context.details.entryPoint.isNotBlank()) return context.details.entryPoint

        val srcRoot = context.taskDir.resolve("src")
        if (Files.exists(srcRoot)) {
            Files.walk(srcRoot).use { stream ->
                val mainClass = stream
                    .filter { Files.isRegularFile(it) && it.fileName.toString().endsWith(".java") }
                    .filter { file -> Files.readString(file).contains("public static void main") }
                    .findFirst()
                    .orElse(null)

                if (mainClass != null) {
                    return mainClass.fileName.toString().removeSuffix(".java")
                }
            }
        }

        return "Solution"
    }
}

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

    private val providers: List<LanguageRunConfigurationProvider> = listOf(
        JavaRunConfigurationProvider(),
        UnsupportedLanguageRunConfigurationProvider(),
    )

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
