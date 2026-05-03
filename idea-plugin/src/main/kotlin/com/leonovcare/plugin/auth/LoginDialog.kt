package com.leonovcare.plugin.auth

import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBPasswordField
import com.intellij.ui.components.JBTextField
import com.intellij.util.ui.FormBuilder
import javax.swing.JComponent

data class LoginRequest(
    val email: String,
    val password: String,
    val token: String,
) {
    val useTokenAuth: Boolean get() = token.isNotBlank()
}

class LoginDialog : DialogWrapper(true) {
    private val emailField = JBTextField()
    private val passwordField = JBPasswordField()
    private val tokenField = JBPasswordField()

    init {
        title = "Leonov Care Platform"
        init()
    }

    override fun createCenterPanel(): JComponent {
        return FormBuilder.createFormBuilder()
            .addLabeledComponent(JBLabel("Email"), emailField)
            .addLabeledComponent(JBLabel("Password"), passwordField)
            .addSeparator()
            .addLabeledComponent(JBLabel("API Token (optional)"), tokenField)
            .panel
    }

    fun request(): LoginRequest {
        return LoginRequest(
            email = emailField.text.trim(),
            password = String(passwordField.password).trim(),
            token = String(tokenField.password).trim(),
        )
    }
}
