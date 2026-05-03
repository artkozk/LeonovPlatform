package com.leonovcare.plugin.ui

import javax.swing.event.DocumentEvent
import javax.swing.event.DocumentListener

class SimpleDocumentListener(
    private val onUpdate: () -> Unit,
) : DocumentListener {
    override fun insertUpdate(e: DocumentEvent?) = onUpdate()
    override fun removeUpdate(e: DocumentEvent?) = onUpdate()
    override fun changedUpdate(e: DocumentEvent?) = onUpdate()
}
