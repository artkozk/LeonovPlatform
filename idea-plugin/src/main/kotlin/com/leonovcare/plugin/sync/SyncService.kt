package com.leonovcare.plugin.sync

import com.intellij.openapi.components.Service
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.notifications.PlatformNotifications
import com.leonovcare.plugin.settings.PlatformSettings
import com.leonovcare.plugin.task.TaskManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.concurrent.atomic.AtomicBoolean

@Service(Service.Level.PROJECT)
class SyncService(private val project: Project) {

    private val settings = PlatformSettings.getInstance()
    private val authService = AuthService.getInstance()
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val taskManager = TaskManager.getInstance(project)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val syncInProgress = AtomicBoolean(false)
    private val autoSyncStarted = AtomicBoolean(false)

    fun triggerManualSync() {
        runSync(showNotifications = true)
    }

    fun startAutoSync() {
        if (!autoSyncStarted.compareAndSet(false, true)) {
            return
        }

        scope.launch {
            while (true) {
                val state = settings.mutableState()
                val interval = state.autoSyncIntervalMinutes.coerceIn(1, 120)
                delay(interval * 60_000L)
                if (state.autoSyncEnabled) {
                    runSync(showNotifications = false)
                }
            }
        }
    }

    private fun runSync(showNotifications: Boolean) {
        if (!syncInProgress.compareAndSet(false, true)) {
            return
        }

        if (authService.token() == null) {
            syncInProgress.set(false)
            return
        }

        scope.launch {
            runCatching {
                val syncResult = authService.withAuthorizedToken { token ->
                    apiFactory.client().sync(token)
                }
                taskManager.refreshAll()
                settings.mutableState().lastSyncEpochMillis = System.currentTimeMillis()
                syncResult
            }.onSuccess { result ->
                if (showNotifications) {
                    PlatformNotifications.syncInfo(project, "Sync completed: updated ${result.updatedTasks} tasks")
                }
            }.onFailure { ex ->
                if (showNotifications) {
                    PlatformNotifications.syncError(project, ex.message ?: "Sync failed")
                }
            }
            syncInProgress.set(false)
        }
    }

    companion object {
        fun getInstance(project: Project): SyncService = project.getService(SyncService::class.java)
    }
}
