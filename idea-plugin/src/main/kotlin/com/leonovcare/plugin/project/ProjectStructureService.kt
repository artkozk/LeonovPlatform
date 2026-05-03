package com.leonovcare.plugin.project

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import java.nio.file.Path

@Service(Service.Level.PROJECT)
class ProjectStructureService(private val project: Project) {
    fun projectRoot(): Path = Path.of(project.basePath ?: error("Project base path is missing"))
    fun tasksRoot(): Path = projectRoot().resolve("platform-tasks")

    companion object {
        fun getInstance(project: Project): ProjectStructureService = project.getService(ProjectStructureService::class.java)
    }
}
