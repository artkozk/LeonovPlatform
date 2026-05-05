package com.leonovcare.plugin.ui

import com.intellij.ui.ColoredListCellRenderer
import com.intellij.ui.SimpleTextAttributes
import com.leonovcare.plugin.task.TaskStatus
import javax.swing.JList

class TaskListRenderer : ColoredListCellRenderer<TaskListEntry>() {
    override fun customizeCellRenderer(
        list: JList<out TaskListEntry>,
        value: TaskListEntry?,
        index: Int,
        selected: Boolean,
        hasFocus: Boolean,
    ) {
        if (value == null) return

        if (value is TaskListEntry.ModuleHeader) {
            append(value.title, SimpleTextAttributes.REGULAR_BOLD_ATTRIBUTES)
            return
        }

        if (value is TaskListEntry.LessonHeader) {
            append("  ${value.title}", SimpleTextAttributes.GRAYED_ATTRIBUTES)
            return
        }

        val task = (value as? TaskListEntry.TaskItem)?.task ?: return

        val statusText = when (task.status) {
            TaskStatus.NEW -> "NEW"
            TaskStatus.IN_PROGRESS -> "IN_PROGRESS"
            TaskStatus.SOLVED -> "SOLVED"
            TaskStatus.FAILED -> "FAILED"
            TaskStatus.LOCKED -> "LOCKED"
            TaskStatus.UNAVAILABLE -> "UNAVAILABLE"
            TaskStatus.UNKNOWN -> "UNKNOWN"
        }

        val attrs = when (task.status) {
            TaskStatus.SOLVED -> SimpleTextAttributes.REGULAR_BOLD_ATTRIBUTES
            TaskStatus.LOCKED, TaskStatus.UNAVAILABLE -> SimpleTextAttributes.GRAYED_ATTRIBUTES
            else -> SimpleTextAttributes.REGULAR_ATTRIBUTES
        }

        append("    ${task.order}. ${task.title}", attrs)
        append("  [$statusText]", SimpleTextAttributes.GRAYED_ATTRIBUTES)
    }
}
