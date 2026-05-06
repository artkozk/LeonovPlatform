package com.leonovcare.plugin.task

import com.intellij.openapi.application.ApplicationNamesInfo
import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.LocalFileSystem
import com.leonovcare.plugin.api.Course
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.PlatformApiClient
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

    private data class StartupSelection(
        val selectedCourseId: String?,
        val selectedCourseTasks: List<Task>,
        val startupTask: Task?,
        val preferredLanguage: TaskLanguage?,
    )

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
    private val startupBootstrapTimeoutMillis = TimeUnit.MILLISECONDS.toMillis(4500)
    private val maxLessonPrefetchPerRefresh = 24
    private val refreshMutex = Mutex()

    @Volatile
    private var startupTaskAutoOpenInFlight = false

    @Volatile
    private var startupTaskAutoOpenedId: String? = null

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val stateFlow = MutableStateFlow(TaskManagerState())

    fun state(): StateFlow<TaskManagerState> = stateFlow.asStateFlow()

    fun initializeFromCache() {
        val courses = courseCache.getCourses()
        val tasksByCourse = normalizeTasksByCourse(taskCache.getTasksByCourse())
        val selection = resolveStartupSelection(courses = courses, tasksByCourse = tasksByCourse)

        settings.mutableState().selectedCourseId = selection.selectedCourseId
        stateFlow.value = TaskManagerState(
            loading = false,
            courses = courses,
            selectedCourseId = selection.selectedCourseId,
            tasks = selection.selectedCourseTasks,
            offlineMode = courses.isNotEmpty() || selection.selectedCourseTasks.isNotEmpty(),
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
                        val preferredLanguage = preferredLanguageForCurrentIde()
                        val state = settings.mutableState()
                        val cachedTasksByCourse = normalizeTasksByCourse(taskCache.getTasksByCourse())
                        val tasksByCourse = cachedTasksByCourse.toMutableMap()

                        if (!hasVisibleData) {
                            val startupBootstrap = runCatching {
                                withTimeout(startupBootstrapTimeoutMillis) {
                                    client.getStartupBootstrap(
                                        token = token,
                                        preferredLanguage = preferredLanguage?.apiName,
                                        selectedCourseId = state.selectedCourseId,
                                        currentTaskId = state.currentTaskId,
                                    )
                                }
                            }.onFailure { ex ->
                                logger.warn("Startup bootstrap failed: ${ex.message}")
                            }.getOrNull()

                            if (startupBootstrap != null && startupBootstrap.courses.isNotEmpty()) {
                                val bootstrapSelectedCourseId = startupBootstrap.selectedCourseId
                                    ?: startupBootstrap.courses.firstOrNull()?.id
                                if (bootstrapSelectedCourseId != null) {
                                    tasksByCourse[bootstrapSelectedCourseId] = normalizeTasks(startupBootstrap.tasks)
                                }

                                state.selectedCourseId = bootstrapSelectedCourseId
                                state.lastSyncEpochMillis = System.currentTimeMillis()
                                courseCache.saveCourses(startupBootstrap.courses)
                                taskCache.saveTasksByCourse(tasksByCourse)

                                val bootstrapSelection = resolveStartupSelection(
                                    courses = startupBootstrap.courses,
                                    tasksByCourse = tasksByCourse,
                                    preferredLanguage = preferredLanguage,
                                )
                                state.selectedCourseId = bootstrapSelection.selectedCourseId
                                stateFlow.value = TaskManagerState(
                                    loading = false,
                                    courses = startupBootstrap.courses,
                                    selectedCourseId = bootstrapSelection.selectedCourseId,
                                    tasks = bootstrapSelection.selectedCourseTasks,
                                    offlineMode = false,
                                )
                                maybeAutoOpenStartupTask(
                                    startupTask = bootstrapSelection.startupTask,
                                    selectedCourseTasks = bootstrapSelection.selectedCourseTasks,
                                )
                            }
                        }

                        val courses = withTimeout(requestTimeoutMillis) {
                            client.getCourses(token)
                        }

                        val cacheSelection = resolveStartupSelection(
                            courses = courses,
                            tasksByCourse = tasksByCourse,
                            preferredLanguage = preferredLanguage,
                        )
                        val selectedCourseId = cacheSelection.selectedCourseId

                        state.selectedCourseId = selectedCourseId
                        state.lastSyncEpochMillis = System.currentTimeMillis()
                        courseCache.saveCourses(courses)
                        taskCache.saveTasksByCourse(tasksByCourse)

                        // Render course shell immediately from cache so user is not blocked by full refresh.
                        stateFlow.value = TaskManagerState(
                            loading = false,
                            courses = courses,
                            selectedCourseId = selectedCourseId,
                            tasks = cacheSelection.selectedCourseTasks,
                            offlineMode = false,
                        )

                        var selectedCourseError: String? = null
                        if (selectedCourseId != null) {
                            val selectedRemote = runCatching {
                                withTimeout(requestTimeoutMillis) {
                                    client.getCourseTasks(token, selectedCourseId)
                                }
                            }.onFailure { ex ->
                                selectedCourseError = ex.message ?: "Failed to load tasks"
                                logger.warn("Failed to load selected course tasks ($selectedCourseId): ${ex.message}")
                            }.getOrNull()

                            if (selectedRemote != null) {
                                val mergedSelected = SyncStatusMerger.merge(
                                    existingTasks = tasksByCourse[selectedCourseId].orEmpty(),
                                    remoteTasks = selectedRemote,
                                ).tasks
                                tasksByCourse[selectedCourseId] = normalizeTasks(mergedSelected)
                                taskCache.saveTasksByCourse(tasksByCourse)
                            }
                        }

                        val finalSelection = resolveStartupSelection(
                            courses = courses,
                            tasksByCourse = tasksByCourse,
                            preferredLanguage = cacheSelection.preferredLanguage,
                        )
                        settings.mutableState().selectedCourseId = finalSelection.selectedCourseId
                        stateFlow.value = stateFlow.value.copy(
                            selectedCourseId = finalSelection.selectedCourseId,
                            tasks = finalSelection.selectedCourseTasks,
                            errorMessage = if (finalSelection.selectedCourseTasks.isEmpty()) selectedCourseError else null,
                            offlineMode = selectedCourseError != null,
                        )

                        // Open startup task immediately after selected course is ready.
                        maybeAutoOpenStartupTask(
                            startupTask = finalSelection.startupTask,
                            selectedCourseTasks = finalSelection.selectedCourseTasks,
                        )

                        loadRemainingCourseTasks(
                            token = token,
                            client = client,
                            courses = courses,
                            selectedCourseId = finalSelection.selectedCourseId,
                            cachedTasksByCourse = cachedTasksByCourse,
                            tasksByCourse = tasksByCourse,
                        )

                        val startupAfterBackground = resolveStartupSelection(
                            courses = courses,
                            tasksByCourse = tasksByCourse,
                            preferredLanguage = finalSelection.preferredLanguage,
                        ).startupTask
                        prefetchLessonMaterialsInBackground(
                            tasksByCourse = tasksByCourse,
                            selectedCourseId = finalSelection.selectedCourseId,
                            startupTask = startupAfterBackground,
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
    }

    private suspend fun loadRemainingCourseTasks(
        token: String,
        client: PlatformApiClient,
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

            val merged = SyncStatusMerger.merge(
                existingTasks = cachedTasksByCourse[course.id].orEmpty(),
                remoteTasks = remoteTasks,
            ).tasks
            tasksByCourse[course.id] = normalizeTasks(merged)
            updated = true
        }

        if (!updated) return

        taskCache.saveTasksByCourse(tasksByCourse)
        val selectedNow = stateFlow.value.selectedCourseId ?: settings.mutableState().selectedCourseId
        if (selectedNow != null) {
            settings.mutableState().selectedCourseId = selectedNow
            stateFlow.value = stateFlow.value.copy(
                selectedCourseId = selectedNow,
                tasks = normalizeTasks(tasksByCourse[selectedNow].orEmpty()),
            )
        }
    }

    fun selectCourse(courseId: String) {
        settings.mutableState().selectedCourseId = courseId
        val tasks = normalizeTasks(taskCache.getTasksByCourse()[courseId].orEmpty())
        stateFlow.value = stateFlow.value.copy(selectedCourseId = courseId, tasks = tasks)
    }

    fun openTask(
        task: Task,
        overwriteExistingEditableFiles: Boolean = false,
        onOpened: (CurrentTaskContext) -> Unit = {},
        onError: (Throwable) -> Unit = {},
    ) {
        if (authService.token() == null) {
            onError(IllegalStateException("Authorization is required to open task"))
            return
        }
        val courseId = stateFlow.value.selectedCourseId ?: task.courseId

        scope.launch {
            runCatching {
                authService.withAuthorizedToken { token ->
                    val client = apiFactory.client()
                    val details = withTimeout(requestTimeoutMillis) {
                        client.getTaskDetails(token, task.id)
                    }
                    val template = withTimeout(requestTimeoutMillis) {
                        client.getTaskTemplate(token, task.id)
                    }
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

    private fun prefetchLessonMaterialsInBackground(
        tasksByCourse: Map<String, List<Task>>,
        selectedCourseId: String?,
        startupTask: Task?,
    ) {
        scope.launch {
            runCatching {
                authService.withAuthorizedToken { token ->
                    val client = apiFactory.client()
                    val existingLessons = lessonCache.getLessonsById().toMutableMap()

                    val selectedCourseTasks = selectedCourseId
                        ?.let { tasksByCourse[it].orEmpty() }
                        .orEmpty()
                        .let(::normalizeTasks)

                    val orderedLessonIds = linkedSetOf<String>()
                    startupTask?.lessonId?.let { orderedLessonIds.add(it) }
                    selectedCourseTasks.mapNotNullTo(orderedLessonIds) { it.lessonId }

                    var updated = 0
                    var fetchedCount = 0
                    for (lessonId in orderedLessonIds) {
                        if (fetchedCount >= maxLessonPrefetchPerRefresh) {
                            logger.info("Lesson prefetch limit reached: $maxLessonPrefetchPerRefresh lessons per refresh")
                            break
                        }

                        val cached = existingLessons[lessonId]
                        if (!shouldRefreshLesson(cached)) {
                            continue
                        }

                        val fetched = runCatching {
                            withTimeout(requestTimeoutMillis) {
                                client.getLessonMaterial(token, lessonId)
                            }
                        }.onFailure { ex ->
                            logger.warn("Failed to prefetch lesson material ($lessonId): ${ex.message}")
                        }.getOrNull() ?: continue

                        existingLessons[lessonId] = fetched
                        updated++
                        fetchedCount++
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
        client: PlatformApiClient,
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
            val fetched = withTimeout(requestTimeoutMillis) {
                client.getLessonMaterial(token, lessonId)
            }
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

    private fun maybeAutoOpenStartupTask(
        startupTask: Task?,
        selectedCourseTasks: List<Task>,
    ) {
        if (startupTask == null || !isTaskOpenable(startupTask)) return
        if (authService.token() == null) return
        if (currentTaskService.getCurrentTask()?.task?.id == startupTask.id) return
        if (startupTaskAutoOpenInFlight || startupTaskAutoOpenedId == startupTask.id) return

        val candidates = buildList {
            add(startupTask)
            selectedCourseTasks
                .asSequence()
                .filter(::isTaskOpenable)
                .filter { it.id != startupTask.id }
                .forEach { add(it) }
        }
        if (candidates.isEmpty()) return

        startupTaskAutoOpenInFlight = true
        openStartupCandidate(candidates, index = 0)
    }

    private fun openStartupCandidate(candidates: List<Task>, index: Int) {
        if (index >= candidates.size) {
            startupTaskAutoOpenInFlight = false
            startupTaskAutoOpenedId = null
            logger.warn("Startup task auto-open exhausted candidates without success")
            return
        }

        val candidate = candidates[index]
        openTask(
            task = candidate,
            onOpened = {
                startupTaskAutoOpenedId = candidate.id
                startupTaskAutoOpenInFlight = false
            },
            onError = { ex ->
                logger.warn("Startup task auto-open failed (${candidate.id}): ${ex.message}")
                openStartupCandidate(candidates, index + 1)
            },
        )
    }

    private fun resolveStartupSelection(
        courses: List<Course>,
        tasksByCourse: Map<String, List<Task>>,
        preferredLanguage: TaskLanguage? = preferredLanguageForCurrentIde(),
    ): StartupSelection {
        if (courses.isEmpty()) {
            return StartupSelection(
                selectedCourseId = null,
                selectedCourseTasks = emptyList(),
                startupTask = null,
                preferredLanguage = preferredLanguage,
            )
        }

        val state = settings.mutableState()
        val currentTaskId = state.currentTaskId
        val validCourseIds = courses.asSequence().map { it.id }.toSet()

        val resumeCourseId = currentTaskId
            ?.let { taskId ->
                tasksByCourse.entries.firstOrNull { (_, tasks) ->
                    tasks.any { it.id == taskId }
                }?.key
            }
            ?.takeIf { validCourseIds.contains(it) }

        val selectedFromSettings = state.selectedCourseId?.takeIf { validCourseIds.contains(it) }
        val idePreferredCourseId = preferredLanguage?.let {
            pickCourseForLanguage(courses = courses, tasksByCourse = tasksByCourse, language = it)
        }

        val selectedCourseId = resumeCourseId
            ?: selectedFromSettings
            ?: idePreferredCourseId
            ?: courses.firstOrNull()?.id

        val selectedTasks = normalizeTasks(selectedCourseId?.let { tasksByCourse[it].orEmpty() }.orEmpty())
        val startupTask = pickStartupTask(
            tasks = selectedTasks,
            preferredLanguage = preferredLanguage,
            currentTaskId = currentTaskId,
        )

        return StartupSelection(
            selectedCourseId = selectedCourseId,
            selectedCourseTasks = selectedTasks,
            startupTask = startupTask,
            preferredLanguage = preferredLanguage,
        )
    }

    private fun pickCourseForLanguage(
        courses: List<Course>,
        tasksByCourse: Map<String, List<Task>>,
        language: TaskLanguage,
    ): String? {
        val tasksMatch = courses.firstOrNull { course ->
            tasksByCourse[course.id].orEmpty().any { task ->
                TaskLanguage.fromApi(task.language) == language
            }
        }?.id
        if (tasksMatch != null) return tasksMatch

        return courses.firstOrNull { course ->
            courseMatchesLanguageByText(course, language)
        }?.id
    }

    private fun pickStartupTask(
        tasks: List<Task>,
        preferredLanguage: TaskLanguage?,
        currentTaskId: String?,
    ): Task? {
        if (tasks.isEmpty()) return null

        val openable = tasks.filter(::isTaskOpenable)
        if (openable.isEmpty()) return null

        val resumeTask = currentTaskId?.let { taskId ->
            openable.firstOrNull { it.id == taskId }
        }
        if (resumeTask != null) return resumeTask

        val preferredTask = preferredLanguage
            ?.let { language ->
                openable.firstOrNull { TaskLanguage.fromApi(it.language) == language }
            }
        return preferredTask ?: openable.first()
    }

    private fun isTaskOpenable(task: Task): Boolean {
        return task.status != TaskStatus.LOCKED && task.status != TaskStatus.UNAVAILABLE
    }

    private fun normalizeTasksByCourse(tasksByCourse: Map<String, List<Task>>): Map<String, List<Task>> {
        return tasksByCourse.mapValues { (_, tasks) -> normalizeTasks(tasks) }
    }

    private fun normalizeTasks(tasks: List<Task>): List<Task> {
        return tasks.sortedWith(
            compareBy<Task> { it.order }
                .thenBy { it.lessonTitle.orEmpty() }
                .thenBy { it.title }
                .thenBy { it.id }
        )
    }

    private fun preferredLanguageForCurrentIde(): TaskLanguage? {
        val product = ApplicationNamesInfo.getInstance().fullProductName.lowercase()
        return when {
            product.contains("pycharm") || product.contains("dataspell") -> TaskLanguage.PYTHON
            product.contains("intellij") || product.contains("idea") -> TaskLanguage.JAVA
            product.contains("webstorm") -> TaskLanguage.JAVASCRIPT
            product.contains("datagrip") -> TaskLanguage.SQL
            product.contains("phpstorm") -> TaskLanguage.JAVASCRIPT
            else -> null
        }
    }

    private fun courseMatchesLanguageByText(course: Course, language: TaskLanguage): Boolean {
        val haystack = "${course.title} ${course.description}".lowercase()
        val keywords = when (language) {
            TaskLanguage.PYTHON -> listOf("python", "питон", "пайтон")
            TaskLanguage.JAVA -> listOf("java", "джава", "java core")
            TaskLanguage.KOTLIN -> listOf("kotlin", "котлин")
            TaskLanguage.SQL -> listOf("sql", "postgres", "mysql", "база данных", "database")
            TaskLanguage.JAVASCRIPT -> listOf("javascript", "typescript", "frontend", "node", "жаваскрипт")
            TaskLanguage.UNKNOWN -> emptyList()
        }
        return keywords.any { haystack.contains(it) }
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
