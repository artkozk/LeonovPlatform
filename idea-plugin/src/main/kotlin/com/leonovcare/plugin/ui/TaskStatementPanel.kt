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

        val actions = JPanel(FlowLayout(FlowLayout.LEFT, 6, 0))

        val runButton = JButton(PlatformBundle.message("button.run"))
        runButton.addActionListener { onRun() }
        actions.add(runButton)

        val debugButton = JButton(PlatformBundle.message("button.debug"))
        debugButton.addActionListener { onDebug() }
        actions.add(debugButton)

        val submitButton = JButton(PlatformBundle.message("button.submit"))
        submitButton.addActionListener { onSubmit() }
        actions.add(submitButton)

        val analyzeButton = JButton(PlatformBundle.message("button.analyze"))
        analyzeButton.addActionListener { onAnalyze() }
        actions.add(analyzeButton)

        val aiHintButton = JButton(PlatformBundle.message("button.aiHint"))
        aiHintButton.addActionListener { onAiHint() }
        actions.add(aiHintButton)

        val referenceButton = JButton(PlatformBundle.message("button.reference"))
        referenceButton.addActionListener { onReference() }
        actions.add(referenceButton)

        val syncButton = JButton(PlatformBundle.message("button.sync"))
        syncButton.addActionListener { onSync() }
        actions.add(syncButton)

        val restoreButton = JButton(PlatformBundle.message("button.restore"))
        restoreButton.addActionListener { onRestore() }
        actions.add(restoreButton)

        root.add(actions, BorderLayout.NORTH)
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
