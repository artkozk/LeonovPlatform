package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.SubmissionResult
import com.leonovcare.plugin.api.SubmissionStatus
import com.leonovcare.plugin.api.TestResultStatus
import java.awt.BorderLayout
import javax.swing.JPanel

class TaskResultPanel {
    val root: JPanel = JPanel(BorderLayout())
    private val output = JBTextArea()

    init {
        output.isEditable = false
        output.rows = 6
        root.add(JBScrollPane(output), BorderLayout.CENTER)
        root.isVisible = false
    }

    fun setResult(result: SubmissionResult?) {
        if (result == null) {
            root.isVisible = false
            output.text = ""
            return
        }
        val statusLabel = when (result.status) {
            SubmissionStatus.QUEUED -> "В очереди"
            SubmissionStatus.RUNNING -> "Выполняется…"
            SubmissionStatus.PASSED -> "✓ Пройдено"
            SubmissionStatus.FAILED -> "✗ Не сдано"
            SubmissionStatus.ERROR -> "Ошибка"
            SubmissionStatus.TIMEOUT -> "Превышено время"
        }
        output.text = buildString {
            appendLine("Статус: $statusLabel")
            if (result.score != null || result.maxScore != null) {
                appendLine("Баллы: ${result.score ?: "—"}/${result.maxScore ?: "—"}")
            }
            if (result.message.isNotBlank()) appendLine(result.message)
            if (result.testResults.isNotEmpty()) {
                appendLine()
                appendLine("Тесты (${result.testResults.count { it.status == TestResultStatus.PASSED }}/${result.testResults.size} пройдено):")
                result.testResults.take(20).forEach { test ->
                    val icon = when (test.status) {
                        TestResultStatus.PASSED -> "✓"
                        TestResultStatus.FAILED -> "✗"
                        TestResultStatus.ERROR -> "!"
                        TestResultStatus.SKIPPED -> "—"
                    }
                    append("  $icon ${test.name}")
                    if (test.status != TestResultStatus.PASSED && test.message.isNotBlank()) {
                        append(": ${test.message.take(120)}")
                    }
                    appendLine()
                }
                if (result.testResults.size > 20) appendLine("  … ещё ${result.testResults.size - 20} тестов")
            }
        }
        output.caretPosition = 0
        root.isVisible = true
    }
}
