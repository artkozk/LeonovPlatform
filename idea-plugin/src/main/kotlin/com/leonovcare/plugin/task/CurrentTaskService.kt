package com.leonovcare.plugin.task

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

@Service(Service.Level.PROJECT)
class CurrentTaskService {
    @Volatile
    private var currentTask: CurrentTaskContext? = null
    private val currentTaskFlow = MutableStateFlow<CurrentTaskContext?>(null)

    fun setCurrentTask(context: CurrentTaskContext) {
        currentTask = context
        currentTaskFlow.value = context
    }

    fun getCurrentTask(): CurrentTaskContext? = currentTask
    fun state(): StateFlow<CurrentTaskContext?> = currentTaskFlow.asStateFlow()

    fun clear() {
        currentTask = null
        currentTaskFlow.value = null
    }

    companion object {
        fun getInstance(project: Project): CurrentTaskService = project.getService(CurrentTaskService::class.java)
    }
}
