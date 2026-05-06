package com.leonovcare.plugin.ui

import com.intellij.openapi.options.ShowSettingsUtil
import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBLabel
import com.leonovcare.plugin.ai.AiHintService
import com.leonovcare.plugin.analysis.CodeStyleAnalysisService
import com.leonovcare.plugin.api.Course
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.auth.LoginDialog
import com.leonovcare.plugin.i18n.PlatformBundle
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.project.ProjectRestoreService
import com.leonovcare.plugin.run.TaskRunConfigurationService
import com.leonovcare.plugin.settings.PlatformSettingsConfigurable
import com.leonovcare.plugin.submission.SubmissionResultPanel
import com.leonovcare.plugin.submission.SubmissionService
import com.leonovcare.plugin.sync.SyncService
import com.leonovcare.plugin.task.CurrentTaskService
import com.leonovcare.plugin.task.TaskManager
import com.leonovcare.plugin.task.TaskStatus
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import java.awt.BorderLayout
import java.awt.CardLayout
import java.awt.FlowLayout
import javax.swing.JButton
import javax.swing.JComboBox
import javax.swing.JPanel
import javax.swing.JSplitPane
import javax.swing.SwingUtilities

class PlatformToolWindowPanel(private val project: Project) {

    private val authService = AuthService.getInstance()
    private val taskManager = TaskManager.getInstance(project)
    private val submissionService = SubmissionService.getInstance(project)
    private val runService = TaskRunConfigurationService.getInstance(project)
    private val syncService = SyncService.getInstance(project)
    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val restoreService = ProjectRestoreService.getInstance(project)
    private val codeStyleService = CodeStyleAnalysisService.getInstance(project)
    private val aiHintService = AiHintService.getInstance(project)

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    val root = JPanel(CardLayout())

    private val unauthorizedPanel = JPanel(BorderLayout())
    private val loadingPanel = JPanel(BorderLayout())
    private val readyPanel = JPanel(BorderLayout())
    private val errorPanel = JPanel(BorderLayout())

    private val unauthorizedMessage = JBLabel("Войдите в аккаунт, чтобы загрузить курсы и задачи")
    private val loadingMessage = JBLabel("Загрузка курсов и задач…")
    private val errorMessage = JBLabel("Ошибка загрузки")
    private val userLabel = JBLabel("-")

    private val courseCombo = JComboBox<Course>()

    private val taskListPanel = TaskListPanel { task ->
        if (task.status == TaskStatus.LOCKED || task.status == TaskStatus.UNAVAILABLE) {
            PlatformNotifications.taskInfo(project, "Задача пока недоступна")
            return@TaskListPanel
        }

        statementPanel.showLoading(task.title)
        taskManager.openTask(
            task = task,
            overwriteExistingEditableFiles = false,
            onOpened = { context ->
                SwingUtilities.invokeLater {
                    statementPanel.setTaskDetails(context.details, context.lessonMaterial)
                }
            },
            onError = { ex ->
                SwingUtilities.invokeLater {
                    statementPanel.showError(ex.message ?: "Ошибка открытия задачи")
                }
                PlatformNotifications.taskError(project, ex.message ?: "Ошибка открытия задачи")
            },
        )
    }

    private val resultPanel = TaskResultPanel()

    private val statementPanel = TaskStatementPanel(
        onRun = {
            runCatching { runService.runCurrentTask(debug = false) }
                .onFailure { PlatformNotifications.taskError(project, it.message ?: "Run failed") }
        },
        onDebug = {
            runCatching { runService.runCurrentTask(debug = true) }
                .onFailure { PlatformNotifications.taskError(project, it.message ?: "Debug failed") }
        },
        onSubmit = {
            submissionService.submitCurrentTask { result ->
                result.onSuccess { submission ->
                    PlatformNotifications.submissionInfo(project, "Проверка завершена: ${submission.status}")
                    SwingUtilities.invokeLater {
                        resultPanel.setResult(submission)
                        SubmissionResultPanel(submission).showAndGet()
                    }
                }.onFailure {
                    PlatformNotifications.submissionError(project, it.message ?: "Ошибка проверки")
                }
            }
        },
        onAnalyze = {
            scope.launch {
                runCatching { codeStyleService.analyzeCurrentTask() }
                    .onSuccess { style ->
                        SwingUtilities.invokeLater {
                            PlatformNotifications.taskInfo(
                                project,
                                PlatformBundle.message("status.styleIssues", style.items.size),
                            )
                        }
                    }
                    .onFailure {
                        SwingUtilities.invokeLater {
                            PlatformNotifications.taskError(project, it.message ?: PlatformBundle.message("status.analysisError"))
                        }
                    }
            }
        },
        onAiHint = {
            fun requestHint() {
                aiHintService.requestHintForCurrentTask { result ->
                    SwingUtilities.invokeLater {
                        result.onSuccess { response ->
                            AiHintDialog(project, response).showAndGet()
                        }.onFailure {
                            PlatformNotifications.taskError(project, it.message ?: PlatformBundle.message("status.aiHintError"))
                        }
                    }
                }
            }

            if (currentTaskService.getCurrentTask() == null) {
                val candidate = firstOpenableTaskFromState()
                if (candidate == null) {
                    PlatformNotifications.taskError(project, PlatformBundle.message("errors.taskUnavailable"))
                    return@TaskStatementPanel
                }
                taskManager.openTask(
                    task = candidate,
                    overwriteExistingEditableFiles = false,
                    onOpened = { requestHint() },
                    onError = { ex ->
                        PlatformNotifications.taskError(project, ex.message ?: PlatformBundle.message("errors.taskUnavailable"))
                    },
                )
                return@TaskStatementPanel
            }

            requestHint()
        },
        onReference = {
            fun showReference() {
                val context = currentTaskService.getCurrentTask()
                if (context == null) {
                    PlatformNotifications.taskError(project, PlatformBundle.message("errors.taskUnavailable"))
                    return
                }

                scope.launch {
                    runCatching {
                        val reference = authService.withAuthorizedToken { token ->
                            PlatformApiClientFactory.getInstance()
                                .client()
                                .getReferenceSolution(token, context.task.id)
                        }

                        SwingUtilities.invokeLater {
                            if (!reference.available) {
                                PlatformNotifications.taskInfo(project, reference.unavailableReason ?: "Эталонное решение недоступно")
                            } else {
                                ReferenceSolutionViewer(project, reference).showAndGet()
                            }
                        }
                    }.onFailure {
                        SwingUtilities.invokeLater {
                            PlatformNotifications.taskError(project, it.message ?: "Ошибка получения эталона")
                        }
                    }
                }
            }

            if (currentTaskService.getCurrentTask() == null) {
                val candidate = firstOpenableTaskFromState()
                if (candidate == null) {
                    PlatformNotifications.taskError(project, PlatformBundle.message("errors.taskUnavailable"))
                    return@TaskStatementPanel
                }
                taskManager.openTask(
                    task = candidate,
                    overwriteExistingEditableFiles = false,
                    onOpened = { showReference() },
                    onError = { ex ->
                        PlatformNotifications.taskError(project, ex.message ?: PlatformBundle.message("errors.taskUnavailable"))
                    },
                )
                return@TaskStatementPanel
            }

            showReference()
        },
        onSync = {
            syncService.triggerManualSync()
        },
        onRestore = {
            val restored = restoreService.restoreCurrentTask(overwriteEditable = false)
            if (restored.restored) {
                PlatformNotifications.taskInfo(project, restored.message)
            } else {
                PlatformNotifications.taskError(project, restored.message)
            }
        },
    )

    init {
        buildUnauthorizedPanel()
        buildLoadingPanel()
        buildReadyPanel()
        buildErrorPanel()

        root.add(unauthorizedPanel, "unauthorized")
        root.add(loadingPanel, "loading")
        root.add(readyPanel, "ready")
        root.add(errorPanel, "error")

        bindState()

        authService.restoreSession()
        taskManager.initializeFromCache()
        taskManager.refreshAll()
        syncService.startAutoSync()
    }

    private fun buildUnauthorizedPanel() {
        val button = JButton("Войти")
        button.addActionListener {
            val dialog = LoginDialog()
            if (!dialog.showAndGet()) return@addActionListener

            val request = dialog.request()
            val onResult: (Result<Unit>) -> Unit = { result ->
                SwingUtilities.invokeLater {
                    result.onSuccess {
                        PlatformNotifications.authInfo(project, "Вход выполнен")
                        taskManager.refreshAll()
                    }.onFailure {
                        PlatformNotifications.authError(project, it.message ?: "Ошибка авторизации")
                    }
                }
            }

            if (request.useTokenAuth) {
                authService.loginWithToken(request.token, onResult)
                return@addActionListener
            }
            if (request.email.isBlank() || request.password.isBlank()) {
                PlatformNotifications.authError(project, "Введите email и пароль")
                return@addActionListener
            }
            authService.loginWithCredentials(request.email, request.password, onResult)
        }

        val settingsButton = JButton("Настройки")
        settingsButton.addActionListener {
            ShowSettingsUtil.getInstance().showSettingsDialog(project, PlatformSettingsConfigurable::class.java)
        }

        val controls = JPanel(FlowLayout(FlowLayout.LEFT, 8, 8))
        controls.add(button)
        controls.add(settingsButton)

        unauthorizedPanel.add(unauthorizedMessage, BorderLayout.CENTER)
        unauthorizedPanel.add(controls, BorderLayout.SOUTH)
    }

    private fun buildLoadingPanel() {
        loadingPanel.add(loadingMessage, BorderLayout.CENTER)
    }

    private fun buildErrorPanel() {
        val retryButton = JButton("Повторить")
        retryButton.addActionListener { taskManager.refreshAll() }

        val settingsButton = JButton("Открыть настройки")
        settingsButton.addActionListener {
            ShowSettingsUtil.getInstance().showSettingsDialog(project, PlatformSettingsConfigurable::class.java)
        }

        val loginAgainButton = JButton("Войти заново")
        loginAgainButton.addActionListener { authService.logout() }

        val controls = JPanel(FlowLayout(FlowLayout.LEFT, 8, 8))
        controls.add(retryButton)
        controls.add(settingsButton)
        controls.add(loginAgainButton)

        errorPanel.add(errorMessage, BorderLayout.CENTER)
        errorPanel.add(controls, BorderLayout.SOUTH)
    }

    private fun buildReadyPanel() {
        val top = JPanel(FlowLayout(FlowLayout.LEFT, 8, 4))

        courseCombo.renderer = CourseComboRenderer()
        courseCombo.addActionListener {
            val selected = courseCombo.selectedItem as? Course ?: return@addActionListener
            taskManager.selectCourse(selected.id)
        }

        val syncButton = JButton("Синхронизировать")
        syncButton.addActionListener { syncService.triggerManualSync() }

        val settingsButton = JButton("Настройки")
        settingsButton.addActionListener {
            ShowSettingsUtil.getInstance().showSettingsDialog(project, PlatformSettingsConfigurable::class.java)
        }

        val logoutButton = JButton("Выйти")
        logoutButton.addActionListener {
            authService.logout()
            PlatformNotifications.authInfo(project, "Выход выполнен")
        }

        top.add(userLabel)
        top.add(courseCombo)
        top.add(syncButton)
        top.add(settingsButton)
        top.add(logoutButton)

        val right = JPanel(BorderLayout(8, 8))
        right.add(statementPanel.root, BorderLayout.CENTER)
        right.add(resultPanel.root, BorderLayout.SOUTH)

        val split = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, taskListPanel.root, right)
        split.resizeWeight = 0.35

        readyPanel.add(top, BorderLayout.NORTH)
        readyPanel.add(split, BorderLayout.CENTER)
    }

    private fun bindState() {
        scope.launch {
            authService.state().collectLatest { authState ->
                SwingUtilities.invokeLater {
                    if (!authState.authorized) {
                        currentTaskService.clear()
                        statementPanel.setTaskDetails(null, null)
                        showCard("unauthorized")
                    } else {
                        userLabel.text = "${authState.userProfile?.displayName ?: "User"} (${authState.userProfile?.email ?: ""})"
                        if (taskManager.state().value.loading) {
                            showCard("loading")
                        } else {
                            showCard("ready")
                        }
                    }
                }
            }
        }

        scope.launch {
            taskManager.state().collectLatest { taskState ->
                SwingUtilities.invokeLater {
                    val hasVisibleData = taskState.courses.isNotEmpty() || taskState.tasks.isNotEmpty()
                    if (taskState.loading && authService.state().value.authorized && !hasVisibleData) {
                        showCard("loading")
                    } else if (taskState.errorMessage != null && authService.state().value.authorized && taskState.tasks.isEmpty()) {
                        errorMessage.text = taskState.errorMessage
                        showCard("error")
                    } else if (authService.state().value.authorized) {
                        updateCourseCombo(taskState.courses, taskState.selectedCourseId)
                        taskListPanel.setTasks(taskState.tasks)
                        showCard("ready")
                    }
                }
            }
        }

        scope.launch {
            submissionService.latestResult().collectLatest { result ->
                SwingUtilities.invokeLater {
                    resultPanel.setResult(result)
                }
            }
        }

        scope.launch {
            currentTaskService.state().collectLatest { context ->
                SwingUtilities.invokeLater {
                    statementPanel.setTaskDetails(context?.details, context?.lessonMaterial)
                }
            }
        }
    }

    private fun updateCourseCombo(courses: List<Course>, selectedCourseId: String?) {
        val selectedBefore = (courseCombo.selectedItem as? Course)?.id

        courseCombo.removeAllItems()
        courses.forEach { courseCombo.addItem(it) }

        val targetId = selectedCourseId ?: selectedBefore
        if (targetId != null) {
            for (index in 0 until courseCombo.itemCount) {
                val item = courseCombo.getItemAt(index)
                if (item.id == targetId) {
                    courseCombo.selectedIndex = index
                    break
                }
            }
        }
    }

    private fun firstOpenableTaskFromState(): Task? {
        return taskManager.state().value.tasks.firstOrNull { task ->
            task.status != TaskStatus.LOCKED && task.status != TaskStatus.UNAVAILABLE
        }
    }

    private fun showCard(name: String) {
        val layout = root.layout as CardLayout
        layout.show(root, name)
    }
}
