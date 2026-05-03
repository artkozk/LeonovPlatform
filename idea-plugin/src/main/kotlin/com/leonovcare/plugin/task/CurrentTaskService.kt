package com.leonovcare.plugin.task

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project

@Service(Service.Level.PROJECT)
class CurrentTaskService {
    @Volatile
    private var currentTask: CurrentTaskContext? = null

    fun setCurrentTask(context: CurrentTaskContext) {
        currentTask = context
    }

    fun getCurrentTask(): CurrentTaskContext? = currentTask

    companion object {
        fun getInstance(project: Project): CurrentTaskService = project.getService(CurrentTaskService::class.java)
    }
}
