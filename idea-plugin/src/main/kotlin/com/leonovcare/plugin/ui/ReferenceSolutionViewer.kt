package com.leonovcare.plugin.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.ReferenceSolution
import com.leonovcare.plugin.task.CurrentTaskService
import java.awt.BorderLayout
import java.awt.GridLayout
import java.nio.file.Files
import javax.swing.JComboBox
import javax.swing.JComponent
import javax.swing.JPanel

class ReferenceSolutionViewer(
    private val project: Project,
    private val referenceSolution: ReferenceSolution,
) : DialogWrapper(project) {

    init {
        title = "Эталонное решение"
        init()
    }

    override fun createCenterPanel(): JComponent {
        val current = CurrentTaskService.getInstance(project).getCurrentTask()

        val userArea = JBTextArea().apply {
            isEditable = false
            text = runCatching {
                val userFile = current?.details?.mainFilePath ?: ""
                val filePath = current?.taskDir?.resolve(userFile)
                if (filePath != null && Files.exists(filePath)) Files.readString(filePath) else ""
            }.getOrDefault("")
        }

        val refArea = JBTextArea().apply {
            isEditable = false
            text = referenceSolution.files.firstOrNull()?.content ?: "Эталон недоступен"
        }

        val selector = JComboBox(referenceSolution.files.map { it.path }.toTypedArray())
        selector.addActionListener {
            val selectedPath = selector.selectedItem as? String ?: return@addActionListener
            val selected = referenceSolution.files.firstOrNull { it.path == selectedPath }
            refArea.text = selected?.content ?: ""
            refArea.caretPosition = 0
        }

        val rightPanel = JPanel(BorderLayout(4, 4))
        rightPanel.add(selector, BorderLayout.NORTH)
        rightPanel.add(JBScrollPane(refArea), BorderLayout.CENTER)

        val panel = JPanel(GridLayout(1, 2, 8, 8))
        panel.add(JBScrollPane(userArea))
        panel.add(rightPanel)
        return panel
    }
}
