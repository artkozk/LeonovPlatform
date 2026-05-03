package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextField
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.task.TaskStatus
import java.awt.BorderLayout
import java.awt.FlowLayout
import javax.swing.DefaultListModel
import javax.swing.JButton
import javax.swing.JComboBox
import javax.swing.JList
import javax.swing.JPanel
import javax.swing.ListSelectionModel

enum class TaskFilter {
    ALL,
    NEW,
    IN_PROGRESS,
    SOLVED,
    UNAVAILABLE,
}

class TaskListPanel(
    private val onTaskOpen: (Task) -> Unit,
) {

    val root: JPanel = JPanel(BorderLayout(8, 8))

    private val model = DefaultListModel<Task>()
    private val list = JList(model)
    private val searchField = JBTextField()
    private val filterCombo = JComboBox(TaskFilter.entries.toTypedArray())

    private var allTasks: List<Task> = emptyList()

    init {
        list.selectionMode = ListSelectionModel.SINGLE_SELECTION
        list.cellRenderer = TaskListRenderer()

        val top = JPanel(FlowLayout(FlowLayout.LEFT, 8, 0))
        top.add(JBLabel("Фильтр"))
        top.add(filterCombo)
        top.add(JBLabel("Поиск"))
        searchField.columns = 16
        top.add(searchField)

        val openButton = JButton("Открыть")
        openButton.addActionListener {
            list.selectedValue?.let { onTaskOpen(it) }
        }
        top.add(openButton)

        filterCombo.addActionListener { applyFilters() }
        searchField.document.addDocumentListener(SimpleDocumentListener { applyFilters() })

        root.add(top, BorderLayout.NORTH)
        root.add(JBScrollPane(list), BorderLayout.CENTER)
    }

    fun setTasks(tasks: List<Task>) {
        allTasks = tasks
        applyFilters()
    }

    private fun applyFilters() {
        val filter = filterCombo.selectedItem as? TaskFilter ?: TaskFilter.ALL
        val query = searchField.text.trim().lowercase()

        val filtered = allTasks.filter { task ->
            val byFilter = when (filter) {
                TaskFilter.ALL -> true
                TaskFilter.NEW -> task.status == TaskStatus.NEW
                TaskFilter.IN_PROGRESS -> task.status == TaskStatus.IN_PROGRESS
                TaskFilter.SOLVED -> task.status == TaskStatus.SOLVED
                TaskFilter.UNAVAILABLE -> task.status == TaskStatus.LOCKED || task.status == TaskStatus.UNAVAILABLE
            }
            val byQuery = query.isBlank() || task.title.lowercase().contains(query)
            byFilter && byQuery
        }

        model.clear()
        filtered.forEach { model.addElement(it) }
    }
}
