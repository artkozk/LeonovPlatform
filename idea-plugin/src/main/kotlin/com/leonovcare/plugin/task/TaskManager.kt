package com.leonovcare.plugin.task

import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.LocalFileSystem
import com.leonovcare.plugin.api.Course
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.PlatformApiClientFactory
import com.leonovcare.plugin.api.Task
import com.leonovcare.plugin.auth.AuthService
import com.leonovcare.plugin.cache.CourseCache
import com.leonovcare.plugin.cache.LessonCache
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
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withTimeout
import java.util.concurrent.TimeUnit

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
    private val lessonCache = LessonCache.getInstance()

    private val lessonCacheTtlMillis = TimeUnit.HOURS.toMillis(8)
    private val requestTimeoutMillis = TimeUnit.SECONDS.toMillis(12)
    private val refreshMutex = Mutex()

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
            refreshMutex.withLock {
                val current = stateFlow.value
                val hasVisibleData = current.courses.isNotEmpty() || current.tasks.isNotEmpty()
                stateFlow.value = current.copy(
                    loading = !hasVisibleData,
                    errorMessage = null,
                )

                runCatching {
                    authService.withAuthorizedToken { token ->
                        val client = apiFactory.client()
                        val courses = withTimeout(requestTimeoutMillis) {
                            client.getCourses(token)
                        }
                        val selectedCourseId = settings.mutableState().selectedCourseId ?: courses.firstOrNull()?.id
                        val cachedTasksByCourse = taskCache.getTasksByCourse()
                        val tasksByCourse = cachedTasksByCourse.toMutableMap()

                        var selectedCourseError: String? = null
                        if (selectedCourseId != null) {
                            val selectedCached = cachedTasksByCourse[selectedCourseId].orEmpty()
                            val selectedRemote = runCatching {
                                withTimeout(requestTimeoutMillis) {
                                    client.getCourseTasks(token, selectedCourseId)
                                }
                            }.onFailure { ex ->
                                selectedCourseError = ex.message ?: "Failed to load tasks"
                                logger.warn("Failed to load selected course tasks ($selectedCourseId): ${ex.message}")
                            }.getOrNull()

                            if (selectedRemote != null) {
                                tasksByCourse[selectedCourseId] = SyncStatusMerger.merge(
                                    existingTasks = selectedCached,
                                    remoteTasks = selectedRemote,
                                ).tasks
                            }
                        }

                        settings.mutableState().selectedCourseId = selectedCourseId
                        settings.mutableState().lastSyncEpochMillis = System.currentTimeMillis()
                        courseCache.saveCourses(courses)
                        taskCache.saveTasksByCourse(tasksByCourse)

                        val selectedTasks = selectedCourseId?.let { tasksByCourse[it] }.orEmpty()
                        stateFlow.value = TaskManagerState(
                            loading = false,
                            courses = courses,
                            selectedCourseId = selectedCourseId,
                            tasks = selectedTasks,
                            errorMessage = if (selectedTasks.isEmpty()) selectedCourseError else null,
                            offlineMode = selectedCourseError != null,
                        )

                        // Finish loading remaining courses in background without blocking initial UI.
                        loadRemainingCourseTasks(
                            token = token,
                            client = client,
                            courses = courses,
                            selectedCourseId = selectedCourseId,
                            cachedTasksByCourse = cachedTasksByCourse,
                            tasksByCourse = tasksByCourse,
                        )

                        prefetchLessonMaterialsInBackground(tasksByCourse.values.flatten())
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
    }

    private suspend fun loadRemainingCourseTasks(
        token: String,
        client: com.leonovcare.plugin.api.PlatformApiClient,
        courses: List<Course>,
        selectedCourseId: String?,
        cachedTasksByCourse: Map<String, List<Task>>,
        tasksByCourse: MutableMap<String, List<Task>>,
    ) {
        if (courses.isEmpty()) return

        var updated = false
        for (course in courses) {
            if (course.id == selectedCourseId) continue

            val remoteTasks = runCatching {
                withTimeout(requestTimeoutMillis) {
                    client.getCourseTasks(token, course.id)
                }
            }.onFailure { ex ->
                logger.warn("Failed to load course tasks (${course.id}): ${ex.message}")
            }.getOrNull() ?: continue

            tasksByCourse[course.id] = SyncStatusMerger.merge(
                existingTasks = cachedTasksByCourse[course.id].orEmpty(),
                remoteTasks = remoteTasks,
            ).tasks
            updated = true
        }

        if (!updated) return

        taskCache.saveTasksByCourse(tasksByCourse)
        val selectedNow = settings.mutableState().selectedCourseId
        if (selectedNow != null && selectedNow == stateFlow.value.selectedCourseId) {
            stateFlow.value = stateFlow.value.copy(
                tasks = tasksByCourse[selectedNow].orEmpty(),
            )
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
                    val lessonMaterial = getOrLoadLessonMaterial(client = client, token = token, task = task)

                    val result = fileService.createOrUpdateTaskFiles(
                        project = project,
                        courseId = courseId,
                        details = details,
                        template = template,
                        overwriteExistingEditableFiles = overwriteExistingEditableFiles,
                        lessonMaterial = lessonMaterial,
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
                        lessonMaterial = lessonMaterial,
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

    private fun prefetchLessonMaterialsInBackground(tasks: List<Task>) {
        scope.launch {
            runCatching {
                authService.withAuthorizedToken { token ->
                    val client = apiFactory.client()
                    val existingLessons = lessonCache.getLessonsById().toMutableMap()

                    val lessonIds = tasks.mapNotNull { it.lessonId }.toSet()
                    var updated = 0

                    for (lessonId in lessonIds) {
                        val cached = existingLessons[lessonId]
                        if (!shouldRefreshLesson(cached)) {
                            continue
                        }

                        val fetched = client.getLessonMaterial(token, lessonId)
                        existingLessons[lessonId] = fetched
                        updated++
                    }

                    if (updated > 0) {
                        lessonCache.saveLessonsById(existingLessons)
                        logger.info("Lesson materials cache updated: $updated lessons")
                    }
                }
            }.onFailure { ex ->
                logger.warn("Lesson materials prefetch failed: ${ex.message}")
            }
        }
    }

    private suspend fun getOrLoadLessonMaterial(
        client: com.leonovcare.plugin.api.PlatformApiClient,
        token: String,
        task: Task,
    ): LessonMaterial? {
        val lessonId = task.lessonId ?: return lessonCache.findByTaskId(task.id)
        val cachedLessons = lessonCache.getLessonsById().toMutableMap()
        val cached = cachedLessons[lessonId]
        if (!shouldRefreshLesson(cached)) {
            return cached
        }

        return runCatching {
            val fetched = client.getLessonMaterial(token, lessonId)
            cachedLessons[lessonId] = fetched
            lessonCache.saveLessonsById(cachedLessons)
            fetched
        }.onFailure { ex ->
            logger.warn("Unable to fetch lesson material for lessonId=$lessonId: ${ex.message}")
        }.getOrElse {
            cached
        }
    }

    private fun shouldRefreshLesson(lesson: LessonMaterial?): Boolean {
        if (lesson == null) return true
        if (lesson.fetchedAtEpochMillis <= 0L) return true
        val age = System.currentTimeMillis() - lesson.fetchedAtEpochMillis
        return age > lessonCacheTtlMillis
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
