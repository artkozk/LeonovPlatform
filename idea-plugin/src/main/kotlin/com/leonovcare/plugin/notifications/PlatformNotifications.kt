package com.leonovcare.plugin.notifications

import com.intellij.notification.NotificationGroupManager
import com.intellij.notification.NotificationType
import com.intellij.openapi.project.Project
import com.leonovcare.plugin.i18n.PlatformBundle

object PlatformNotifications {

    private val authGroup by lazy { NotificationGroupManager.getInstance().getNotificationGroup(PlatformBundle.message("notifications.auth")) }
    private val tasksGroup by lazy { NotificationGroupManager.getInstance().getNotificationGroup(PlatformBundle.message("notifications.tasks")) }
    private val submissionGroup by lazy { NotificationGroupManager.getInstance().getNotificationGroup(PlatformBundle.message("notifications.submission")) }
    private val syncGroup by lazy { NotificationGroupManager.getInstance().getNotificationGroup(PlatformBundle.message("notifications.sync")) }

    fun authInfo(project: Project?, message: String) {
        authGroup.createNotification(message, NotificationType.INFORMATION).notify(project)
    }

    fun authError(project: Project?, message: String) {
        authGroup.createNotification(message, NotificationType.ERROR).notify(project)
    }

    fun taskInfo(project: Project?, message: String) {
        tasksGroup.createNotification(message, NotificationType.INFORMATION).notify(project)
    }

    fun taskError(project: Project?, message: String) {
        tasksGroup.createNotification(message, NotificationType.ERROR).notify(project)
    }

    fun submissionInfo(project: Project?, message: String) {
        submissionGroup.createNotification(message, NotificationType.INFORMATION).notify(project)
    }

    fun submissionError(project: Project?, message: String) {
        submissionGroup.createNotification(message, NotificationType.ERROR).notify(project)
    }

    fun syncInfo(project: Project?, message: String) {
        syncGroup.createNotification(message, NotificationType.INFORMATION).notify(project)
    }

    fun syncError(project: Project?, message: String) {
        syncGroup.createNotification(message, NotificationType.ERROR).notify(project)
    }
}
