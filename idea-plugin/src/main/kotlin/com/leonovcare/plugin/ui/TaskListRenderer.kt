package com.leonovcare.plugin.ui

import com.intellij.ui.ColoredListCellRenderer
import com.intellij.ui.SimpleTextAttributes
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.task.TaskStatus
import javax.swing.JList

class TaskListRenderer : ColoredListCellRenderer<Task>() {
    override fun customizeCellRenderer(
        list: JList<out Task>,
        value: Task?,
        index: Int,
        selected: Boolean,
        hasFocus: Boolean,
    ) {
        if (value == null) return

        val statusText = when (value.status) {
            TaskStatus.NEW -> "NEW"
            TaskStatus.IN_PROGRESS -> "IN_PROGRESS"
            TaskStatus.SOLVED -> "SOLVED"
            TaskStatus.FAILED -> "FAILED"
            TaskStatus.LOCKED -> "LOCKED"
            TaskStatus.UNAVAILABLE -> "UNAVAILABLE"
            TaskStatus.UNKNOWN -> "UNKNOWN"
        }

        val attrs = when (value.status) {
            TaskStatus.SOLVED -> SimpleTextAttributes.REGULAR_BOLD_ATTRIBUTES
            TaskStatus.LOCKED, TaskStatus.UNAVAILABLE -> SimpleTextAttributes.GRAYED_ATTRIBUTES
            else -> SimpleTextAttributes.REGULAR_ATTRIBUTES
        }

        append("${value.order}. ${value.title}", attrs)
        append("  [$statusText]", SimpleTextAttributes.GRAYED_ATTRIBUTES)
    }
}
