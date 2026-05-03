package com.leonovcare.plugin.ui

import com.intellij.ui.SimpleListCellRenderer
import com.leonovcare.plugin.api.Course
import javax.swing.JList

class CourseComboRenderer : SimpleListCellRenderer<Course>() {
    override fun customize(
        list: JList<out Course>,
        value: Course?,
        index: Int,
        selected: Boolean,
        hasFocus: Boolean,
    ) {
        text = value?.title ?: ""
    }
}
