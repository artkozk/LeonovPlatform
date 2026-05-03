package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.SubmissionResult
import java.awt.BorderLayout
import javax.swing.JPanel

class TaskResultPanel {
    val root: JPanel = JPanel(BorderLayout())
    private val output = JBTextArea()

    init {
        output.isEditable = false
        output.rows = 8
        root.add(JBScrollPane(output), BorderLayout.CENTER)
    }

    fun setResult(result: SubmissionResult?) {
        output.text = if (result == null) {
            ""
        } else {
            buildString {
                appendLine("Статус: ${result.status}")
                appendLine("Score: ${result.score ?: "-"}/${result.maxScore ?: "-"}")
                if (result.message.isNotBlank()) {
                    appendLine(result.message)
                }
                if (result.testResults.isNotEmpty()) {
                    appendLine("Тесты:")
                    result.testResults.forEach { appendLine("- ${it.name}: ${it.status}") }
                }
            }
        }
    }
}
