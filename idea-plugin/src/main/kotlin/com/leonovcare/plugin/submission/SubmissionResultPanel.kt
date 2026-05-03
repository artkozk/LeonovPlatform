package com.leonovcare.plugin.submission

import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.SubmissionResult
import java.awt.BorderLayout
import javax.swing.JComponent
import javax.swing.JPanel

class SubmissionResultPanel(private val result: SubmissionResult) : DialogWrapper(true) {

    init {
        title = "Результат проверки"
        init()
    }

    override fun createCenterPanel(): JComponent {
        val area = JBTextArea()
        area.isEditable = false
        area.text = buildString {
            appendLine("Статус: ${result.status}")
            appendLine("Score: ${result.score ?: "-"}/${result.maxScore ?: "-"}")
            if (result.message.isNotBlank()) {
                appendLine("Сообщение: ${result.message}")
            }
            if (result.testResults.isNotEmpty()) {
                appendLine()
                appendLine("Тесты:")
                result.testResults.forEach { test ->
                    appendLine("- ${test.name}: ${test.status}")
                    if (test.message.isNotBlank()) {
                        appendLine("  ${test.message}")
                    }
                    if (!test.expected.isNullOrBlank() || !test.actual.isNullOrBlank()) {
                        appendLine("  expected=${test.expected}")
                        appendLine("  actual=${test.actual}")
                    }
                }
            }
        }

        val panel = JPanel(BorderLayout())
        panel.add(JBScrollPane(area), BorderLayout.CENTER)
        return panel
    }
}
