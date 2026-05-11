package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.UIUtil
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.LessonMaterialFormatter
import java.awt.BorderLayout
import java.awt.Color
import java.awt.FlowLayout
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JEditorPane
import javax.swing.JPanel

class TaskStatementPanel(
    onRun: () -> Unit,
    onDebug: () -> Unit,
    onSubmit: () -> Unit,
    onAnalyze: () -> Unit,
    onAiHint: () -> Unit,
    onReference: () -> Unit,
    onSync: () -> Unit,
    onRestore: () -> Unit,
) {

    val root: JPanel = JPanel(BorderLayout(8, 8))
    private val statementArea = JEditorPane()

    init {
        statementArea.contentType = "text/html"
        statementArea.isEditable = false
        statementArea.putClientProperty(JEditorPane.HONOR_DISPLAY_PROPERTIES, true)
        statementArea.background = UIUtil.getPanelBackground()
        statementArea.foreground = UIUtil.getLabelForeground()
        statementArea.font = UIUtil.getLabelFont()
        statementArea.isOpaque = true

        val actionsBox = JPanel()
        actionsBox.layout = BoxLayout(actionsBox, BoxLayout.Y_AXIS)

        val primaryRow = JPanel(FlowLayout(FlowLayout.LEFT, 4, 2))
        val runButton = JButton(PlatformBundle.message("button.run"))
        runButton.addActionListener { onRun() }
        primaryRow.add(runButton)

        val debugButton = JButton(PlatformBundle.message("button.debug"))
        debugButton.addActionListener { onDebug() }
        primaryRow.add(debugButton)

        val submitButton = JButton(PlatformBundle.message("button.submit"))
        submitButton.addActionListener { onSubmit() }
        primaryRow.add(submitButton)

        val analyzeButton = JButton(PlatformBundle.message("button.analyze"))
        analyzeButton.addActionListener { onAnalyze() }
        primaryRow.add(analyzeButton)

        val aiHintButton = JButton(PlatformBundle.message("button.aiHint"))
        aiHintButton.addActionListener { onAiHint() }
        primaryRow.add(aiHintButton)

        val referenceButton = JButton(PlatformBundle.message("button.reference"))
        referenceButton.addActionListener { onReference() }
        primaryRow.add(referenceButton)

        val secondaryRow = JPanel(FlowLayout(FlowLayout.LEFT, 4, 2))
        val syncButton = JButton(PlatformBundle.message("button.sync"))
        syncButton.addActionListener { onSync() }
        secondaryRow.add(syncButton)

        val restoreButton = JButton(PlatformBundle.message("button.restore"))
        restoreButton.addActionListener { onRestore() }
        secondaryRow.add(restoreButton)

        actionsBox.add(primaryRow)
        actionsBox.add(secondaryRow)
        root.add(actionsBox, BorderLayout.NORTH)
        root.add(JBScrollPane(statementArea), BorderLayout.CENTER)
    }

    fun setTaskDetails(details: TaskDetails?, lessonMaterial: LessonMaterial? = null) {
        val markdown = LessonMaterialFormatter.buildTaskAndLessonText(details, lessonMaterial)
        statementArea.text = MarkdownHtmlRenderer.render(
            markdown = markdown,
            textColorHex = colorToHex(statementArea.foreground),
            backgroundColorHex = colorToHex(statementArea.background),
        )
        statementArea.caretPosition = 0
    }

    fun showLoading(taskTitle: String?) {
        val title = taskTitle?.trim().takeUnless { it.isNullOrBlank() } ?: "задачи"
        val markdown = "### Загрузка\n\nОткрываем материалы для **$title**…"
        statementArea.text = MarkdownHtmlRenderer.render(
            markdown = markdown,
            textColorHex = colorToHex(statementArea.foreground),
            backgroundColorHex = colorToHex(statementArea.background),
        )
        statementArea.caretPosition = 0
    }

    fun showError(rawMessage: String?) {
        val message = rawMessage?.trim().takeUnless { it.isNullOrBlank() } ?: "Не удалось загрузить материалы задачи."
        val markdown = buildString {
            appendLine("### Ошибка загрузки")
            appendLine()
            appendLine(message)
            appendLine()
            appendLine("Нажмите `Синхронизировать` и попробуйте открыть задачу снова.")
        }
        statementArea.text = MarkdownHtmlRenderer.render(
            markdown = markdown,
            textColorHex = colorToHex(statementArea.foreground),
            backgroundColorHex = colorToHex(statementArea.background),
        )
        statementArea.caretPosition = 0
    }

    private fun colorToHex(color: Color?): String {
        val value = color ?: return "#d8dee9"
        return String.format("#%02x%02x%02x", value.red, value.green, value.blue)
    }
}
