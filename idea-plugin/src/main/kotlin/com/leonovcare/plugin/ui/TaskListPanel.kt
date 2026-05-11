package com.leonovcare.plugin.ui

import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextField
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.task.TaskStatus
import java.awt.BorderLayout
import java.awt.Component
import java.awt.FlowLayout
import java.awt.Point
import java.awt.event.KeyEvent
import java.awt.event.MouseAdapter
import java.awt.event.MouseEvent
import javax.swing.AbstractAction
import javax.swing.DefaultListCellRenderer
import javax.swing.DefaultListModel
import javax.swing.JButton
import javax.swing.JComboBox
import javax.swing.JList
import javax.swing.JPanel
import javax.swing.KeyStroke
import javax.swing.ListSelectionModel

sealed interface TaskListEntry {
    data class ModuleHeader(val title: String) : TaskListEntry
    data class LessonHeader(val title: String) : TaskListEntry
    data class TaskItem(val task: Task) : TaskListEntry
}

enum class TaskFilter(val label: String) {
    ALL("Все"),
    NEW("Новые"),
    IN_PROGRESS("В работе"),
    SOLVED("Решённые"),
    UNAVAILABLE("Недоступные"),
}

class TaskListPanel(
    private val onTaskOpen: (Task) -> Unit,
) {

    val root: JPanel = JPanel(BorderLayout(8, 8))

    private val model = DefaultListModel<TaskListEntry>()
    private val list = JList(model)
    private val searchField = JBTextField()
    private val filterCombo = JComboBox(TaskFilter.entries.toTypedArray()).also { combo ->
        combo.renderer = object : DefaultListCellRenderer() {
            override fun getListCellRendererComponent(
                list: JList<*>?, value: Any?, index: Int, isSelected: Boolean, cellHasFocus: Boolean,
            ): Component {
                super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus)
                text = (value as? TaskFilter)?.label ?: value?.toString() ?: ""
                return this
            }
        }
    }

    private var allTasks: List<Task> = emptyList()

    init {
        list.selectionMode = ListSelectionModel.SINGLE_SELECTION
        list.cellRenderer = TaskListRenderer()
        list.addMouseListener(
            object : MouseAdapter() {
                override fun mouseClicked(e: MouseEvent) {
                    if (e.button == MouseEvent.BUTTON1 && e.clickCount >= 2 && !e.isPopupTrigger) {
                        openTaskAtPoint(e.point)
                    }
                }
            }
        )
        list.inputMap.put(KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0), "open-task")
        list.actionMap.put(
            "open-task",
            object : AbstractAction() {
                override fun actionPerformed(e: java.awt.event.ActionEvent?) {
                    openSelectedTask()
                }
            }
        )

        val top = JPanel(FlowLayout(FlowLayout.LEFT, 8, 0))
        top.add(JBLabel("Фильтр"))
        top.add(filterCombo)
        top.add(JBLabel("Поиск"))
        searchField.columns = 16
        top.add(searchField)

        val openButton = JButton("Открыть")
        openButton.addActionListener {
            openSelectedTask()
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

    fun selectedTaskOrFirstOpenable(): Task? {
        val selected = (list.selectedValue as? TaskListEntry.TaskItem)?.task
        if (selected != null && selected.status != TaskStatus.LOCKED && selected.status != TaskStatus.UNAVAILABLE) {
            return selected
        }
        return allTasks.firstOrNull { it.status != TaskStatus.LOCKED && it.status != TaskStatus.UNAVAILABLE }
    }

    private fun applyFilters() {
        val selectedTaskId = (list.selectedValue as? TaskListEntry.TaskItem)?.task?.id
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
        var currentModule: String? = null
        var currentLesson: String? = null

        filtered.forEach { task ->
            val moduleTitle = moduleTitle(task)
            if (moduleTitle != currentModule) {
                currentModule = moduleTitle
                currentLesson = null
                model.addElement(TaskListEntry.ModuleHeader("Модуль: $moduleTitle"))
            }

            val lessonTitle = lessonTitle(task)
            if (lessonTitle != currentLesson) {
                currentLesson = lessonTitle
                model.addElement(TaskListEntry.LessonHeader("Урок: $lessonTitle"))
            }

            model.addElement(TaskListEntry.TaskItem(task))
        }

        if (selectedTaskId != null) {
            for (index in 0 until model.size) {
                val entry = model.getElementAt(index)
                if (entry is TaskListEntry.TaskItem && entry.task.id == selectedTaskId) {
                    list.selectedIndex = index
                    break
                }
            }
        }
    }

    private fun openSelectedTask() {
        val selectedTask = (list.selectedValue as? TaskListEntry.TaskItem)?.task ?: return
        onTaskOpen(selectedTask)
    }

    private fun openTaskAtPoint(point: Point) {
        val index = list.locationToIndex(point)
        if (index < 0) return

        val cellBounds = list.getCellBounds(index, index) ?: return
        if (!cellBounds.contains(point)) return

        list.selectedIndex = index
        openSelectedTask()
    }

    private fun moduleTitle(task: Task): String {
        return task.moduleId?.trim().takeUnless { it.isNullOrBlank() } ?: "Без модуля"
    }

    private fun lessonTitle(task: Task): String {
        return task.lessonTitle?.trim().takeUnless { it.isNullOrBlank() }
            ?: task.lessonId?.trim()?.takeUnless { it.isBlank() }
            ?: "Без урока"
    }
}
