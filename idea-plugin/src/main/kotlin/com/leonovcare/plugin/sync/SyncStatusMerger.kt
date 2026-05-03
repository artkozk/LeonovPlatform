package com.leonovcare.plugin.sync

import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.task.TaskStatus

data class SyncMergeResult(
    val tasks: List<Task>,
    val changedStatuses: Int,
)

object SyncStatusMerger {

    fun merge(existingTasks: List<Task>, remoteTasks: List<Task>): SyncMergeResult {
        val existingById = existingTasks.associateBy { it.id }
        var changed = 0

        val merged = remoteTasks.map { remote ->
            val existing = existingById[remote.id]
            if (existing == null) {
                remote
            } else {
                val mergedStatus = if (remote.status == TaskStatus.UNKNOWN) existing.status else remote.status
                if (mergedStatus != existing.status) {
                    changed++
                }
                remote.copy(status = mergedStatus)
            }
        }

        return SyncMergeResult(merged, changed)
    }
}
