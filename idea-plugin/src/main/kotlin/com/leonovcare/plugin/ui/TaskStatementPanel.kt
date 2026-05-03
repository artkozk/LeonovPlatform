package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.task.LessonMaterialFormatter
import java.awt.BorderLayout
import java.awt.FlowLayout
import javax.swing.JButton
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
    private val statementArea = JBTextArea()

    init {
        statementArea.isEditable = false
        statementArea.lineWrap = true
        statementArea.wrapStyleWord = true

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
        statementArea.text = LessonMaterialFormatter.buildTaskAndLessonText(details, lessonMaterial)
        statementArea.caretPosition = 0
    }
}
