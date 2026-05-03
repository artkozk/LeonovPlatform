package com.leonovcare.plugin.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.AiHintResponse
import com.leonovcare.plugin.i18n.PlatformBundle
import java.awt.BorderLayout
import javax.swing.JComponent
import javax.swing.JPanel

class AiHintDialog(
    project: Project,
    private val response: AiHintResponse,
) : DialogWrapper(project) {

    init {
        title = PlatformBundle.message("ai.dialog.title")
        init()
    }

    override fun createCenterPanel(): JComponent {
        val panel = JPanel(BorderLayout(8, 8))
        val textArea = JBTextArea()
        textArea.isEditable = false
        textArea.lineWrap = true
        textArea.wrapStyleWord = true
        textArea.text = buildString {
            append(response.hint.trim())
            response.model?.let { model ->
                if (model.isNotBlank()) {
                    append("\n\n")
                    append(PlatformBundle.message("ai.dialog.model", model))
                }
            }
        }
        textArea.caretPosition = 0

        panel.add(JBScrollPane(textArea), BorderLayout.CENTER)
        return panel
    }
}
