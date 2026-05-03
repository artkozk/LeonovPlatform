package com.leonovcare.plugin.task

import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.LocalFileSystem
import com.leonovcare.plugin.api.Course
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.cache.CourseCache
import com.leonovcare.plugin.cache.TaskCache
import com.leonovcare.plugin.settings.PlatformSettings
import com.leonovcare.plugin.sync.SyncStatusMerger
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class TaskManagerState(
    val loading: Boolean = false,
    val courses: List<Course> = emptyList(),
    val selectedCourseId: String? = null,
    val tasks: List<Task> = emptyList(),
    val errorMessage: String? = null,
    val offlineMode: Boolean = false,
)

@Service(Service.Level.PROJECT)
class TaskManager(private val project: Project) {

    private val logger = Logger.getInstance(TaskManager::class.java)
    private val settings = PlatformSettings.getInstance()
    private val authService = AuthService.getInstance()
    private val apiFactory = PlatformApiClientFactory.getInstance()
    private val fileService = TaskFileService()
    private val currentTaskService = CurrentTaskService.getInstance(project)
    private val courseCache = CourseCache.getInstance()
    private val taskCache = TaskCache.getInstance()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val stateFlow = MutableStateFlow(TaskManagerState())

    fun state(): StateFlow<TaskManagerState> = stateFlow.asStateFlow()

    fun initializeFromCache() {
        val state = settings.mutableState()
        val courses = courseCache.getCourses()
        val tasksByCourse = taskCache.getTasksByCourse()
        val selectedCourse = state.selectedCourseId ?: courses.firstOrNull()?.id
        val selectedTasks = selectedCourse?.let { tasksByCourse[it] }.orEmpty()
        stateFlow.value = TaskManagerState(
            loading = false,
            courses = courses,
            selectedCourseId = selectedCourse,
            tasks = selectedTasks,
            offlineMode = courses.isNotEmpty() || selectedTasks.isNotEmpty(),
        )
    }

    fun refreshAll() {
        scope.launch {
            if (authService.token() == null) {
                return@launch
            }
            stateFlow.value = stateFlow.value.copy(loading = true, errorMessage = null)
            runCatching {
                authService.withAuthorizedToken { token ->
                    val client = apiFactory.client()
                    val courses = client.getCourses(token)
                    val selectedCourseId = settings.mutableState().selectedCourseId ?: courses.firstOrNull()?.id
                    val tasksByCourse = mutableMapOf<String, List<Task>>()
                    val cachedTasksByCourse = taskCache.getTasksByCourse()
                    courses.forEach { course ->
                        val remoteTasks = client.getCourseTasks(token, course.id)
                        val mergedTasks = SyncStatusMerger.merge(
                            existingTasks = cachedTasksByCourse[course.id].orEmpty(),
                            remoteTasks = remoteTasks,
                        ).tasks
                        tasksByCourse[course.id] = mergedTasks
                    }

                    settings.mutableState().selectedCourseId = selectedCourseId
                    settings.mutableState().lastSyncEpochMillis = System.currentTimeMillis()
                    courseCache.saveCourses(courses)
                    taskCache.saveTasksByCourse(tasksByCourse)

                    stateFlow.value = TaskManagerState(
                        loading = false,
                        courses = courses,
                        selectedCourseId = selectedCourseId,
                        tasks = selectedCourseId?.let { tasksByCourse[it] }.orEmpty(),
                        offlineMode = false,
                    )
                }
            }.onFailure { ex ->
                logger.warn("Failed to refresh courses/tasks: ${ex.message}")
                val fallback = stateFlow.value
                stateFlow.value = fallback.copy(
                    loading = false,
                    errorMessage = ex.message,
                    offlineMode = true,
                )
            }
        }
    }

    fun selectCourse(courseId: String) {
        settings.mutableState().selectedCourseId = courseId
        val tasks = taskCache.getTasksByCourse()[courseId].orEmpty()
        stateFlow.value = stateFlow.value.copy(selectedCourseId = courseId, tasks = tasks)
    }

    fun openTask(
        task: Task,
        overwriteExistingEditableFiles: Boolean = false,
        onOpened: (CurrentTaskContext) -> Unit = {},
        onError: (Throwable) -> Unit = {},
    ) {
        if (authService.token() == null) return
        val courseId = stateFlow.value.selectedCourseId ?: task.courseId

        scope.launch {
            runCatching {
                authService.withAuthorizedToken { token ->
                    val client = apiFactory.client()
                    val details = client.getTaskDetails(token, task.id)
                    val template = client.getTaskTemplate(token, task.id)

                    val result = fileService.createOrUpdateTaskFiles(
                        project = project,
                        courseId = courseId,
                        details = details,
                        template = template,
                        overwriteExistingEditableFiles = overwriteExistingEditableFiles,
                    )

                    val previousContext = currentTaskService.getCurrentTask()
                    if (settings.mutableState().closeFilesOnTaskSwitch &&
                        previousContext != null &&
                        previousContext.taskDir != result.taskDirectory
                    ) {
                        closeEditorsUnder(previousContext.taskDir)
                    }

                    val localFile = LocalFileSystem.getInstance().refreshAndFindFileByNioFile(result.mainFile)
                    if (localFile != null) {
                        FileEditorManager.getInstance(project).openFile(localFile, true)
                    }

                    val context = CurrentTaskContext(
                        courseId = courseId,
                        task = task,
                        details = details,
                        template = template,
                        taskDir = result.taskDirectory,
                    )
                    currentTaskService.setCurrentTask(context)

                    settings.mutableState().currentTaskId = task.id
                    client.markTaskInProgress(token, task.id)
                    onOpened(context)
                }
            }.onFailure { onError(it) }
        }
    }

    private fun closeEditorsUnder(taskDir: java.nio.file.Path) {
        val editorManager = FileEditorManager.getInstance(project)
        editorManager.openFiles.forEach { file ->
            val nioPath = runCatching { java.nio.file.Path.of(file.path) }.getOrNull() ?: return@forEach
            if (nioPath.normalize().startsWith(taskDir.normalize())) {
                editorManager.closeFile(file)
            }
        }
    }

    companion object {
        fun getInstance(project: Project): TaskManager = project.getService(TaskManager::class.java)
    }
}
