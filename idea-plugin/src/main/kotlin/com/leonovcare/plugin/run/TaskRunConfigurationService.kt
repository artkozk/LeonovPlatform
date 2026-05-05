package com.leonovcare.plugin.run

import com.intellij.execution.RunnerAndConfigurationSettings
import com.intellij.execution.ProgramRunnerUtil
import com.intellij.execution.RunManager
import com.intellij.execution.configurations.ConfigurationFactory
import com.intellij.execution.executors.DefaultDebugExecutor
import com.intellij.execution.executors.DefaultRunExecutor
import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.CurrentTaskContext
import com.leonovcare.plugin.task.TaskLanguage
import com.leonovcare.plugin.task.CurrentTaskService
import java.nio.file.Files

class UnsupportedLanguageRunConfigurationProvider : LanguageRunConfigurationProvider {
    override fun supports(language: String): Boolean = true

    override fun ensureConfiguration(project: Project, context: CurrentTaskContext): RunnerAndConfigurationSettings {
        val language = TaskLanguage.fromApi(context.details.language)
        throw IllegalStateException(
            PlatformBundle.message("errors.unsupportedLanguageWithName", language.apiName),
        )
    }
}

class PythonRunConfigurationProvider : LanguageRunConfigurationProvider {
    override fun supports(language: String): Boolean {
        return TaskLanguage.fromApi(language) == TaskLanguage.PYTHON
    }

    override fun ensureConfiguration(project: Project, context: CurrentTaskContext): RunnerAndConfigurationSettings {
        val scriptPath = context.taskDir.resolve(context.details.mainFilePath).normalize()
        if (!Files.exists(scriptPath)) {
            throw IllegalStateException(
                PlatformBundle.message("errors.pythonMainFileMissing", scriptPath.toString()),
            )
        }

        return runCatching {
            createPythonRunSettings(project = project, context = context, scriptPath = scriptPath.toString())
        }.getOrElse { ex ->
            throw IllegalStateException(
                PlatformBundle.message("errors.pythonRunConfigUnavailable", ex.message ?: "unknown"),
                ex,
            )
        }
    }

    private fun createPythonRunSettings(
        project: Project,
        context: CurrentTaskContext,
        scriptPath: String,
    ): RunnerAndConfigurationSettings {
        val runManager = RunManager.getInstance(project)
        val configurationTypeClass = Class.forName("com.jetbrains.python.run.PythonConfigurationType")
        val configurationType = configurationTypeClass.getMethod("getInstance").invoke(null)
        val factories = configurationType.javaClass.getMethod("getConfigurationFactories")
            .invoke(configurationType) as Array<*>
        val factory = factories.firstOrNull() as? ConfigurationFactory
            ?: error("Python ConfigurationFactory is unavailable")

        val settings = runManager.createConfiguration("LeonovCare: ${context.task.title}", factory)
        val configuration = settings.configuration

        invokeSetter(configuration, "setScriptName", scriptPath)
        invokeSetter(configuration, "setWorkingDirectory", context.taskDir.toString())
        invokeSetter(configuration, "setInterpreterOptions", "")
        invokeSetter(configuration, "setScriptParameters", "")
        invokeSetter(configuration, "setModuleMode", false)

        return settings
    }

    private fun invokeSetter(target: Any, methodName: String, value: Any) {
        val method = target.javaClass.methods.firstOrNull { method ->
            method.name == methodName &&
                method.parameterCount == 1 &&
                method.parameterTypes.firstOrNull()?.isAssignableFrom(value.javaClass) == true
        } ?: target.javaClass.methods.firstOrNull { method ->
            method.name == methodName &&
                method.parameterCount == 1 &&
                method.parameterTypes.firstOrNull() == Boolean::class.javaPrimitiveType &&
                value is Boolean
        } ?: return

        method.isAccessible = true
        method.invoke(target, value)
    }
}

@Service(Service.Level.PROJECT)
class TaskRunConfigurationService(private val project: Project) {

    private val providers: List<LanguageRunConfigurationProvider> = buildList {
        add(PythonRunConfigurationProvider())
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
