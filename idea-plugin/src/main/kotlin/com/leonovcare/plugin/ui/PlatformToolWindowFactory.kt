package com.leonovcare.plugin.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.util.Disposer
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory

class PlatformToolWindowFactory : ToolWindowFactory {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val panel = PlatformToolWindowPanel(project)
        val content = ContentFactory.getInstance().createContent(panel.root, "", false)
        Disposer.register(content, panel)
        toolWindow.contentManager.addContent(content)
    }
}
