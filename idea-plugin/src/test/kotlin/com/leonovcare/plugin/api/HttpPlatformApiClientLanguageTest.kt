package com.leonovcare.plugin.api

import com.sun.net.httpserver.HttpServer
import com.leonovcare.plugin.task.TaskStatus
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.net.InetSocketAddress

class HttpPlatformApiClientLanguageTest {

    private var server: HttpServer? = null

    @AfterEach
    fun tearDown() {
        server?.stop(0)
        server = null
    }

    @Test
    fun `maps sql task details and fallback template path`() {
        startServer()
        val client = HttpPlatformApiClient(baseUrl())

        val details = runBlocking { client.getTaskDetails("token", "task-sql") }
        assertEquals("SQL", details.language)
        assertEquals("src/main/sql/query.sql", details.mainFilePath)
        assertEquals("query.sql", details.entryPoint)

        val template = runBlocking { client.getTaskTemplate("token", "task-sql") }
        assertEquals("src/main/sql/query.sql", template.files.single().path)
    }

    @Test
    fun `maps task lesson metadata from course flow`() {
        startServerForCourseFlow()
        val client = HttpPlatformApiClient(baseUrl())

        val tasks = runBlocking { client.getCourseTasks("token", "course-1") }
        val task = tasks.single()

        assertEquals("lesson-1", task.lessonId)
        assertEquals("Lesson One", task.lessonTitle)
    }

    @Test
    fun `maps task status from tasks catalog`() {
        startServerForCatalogFlow()
        val client = HttpPlatformApiClient(baseUrl())

        val task = runBlocking { client.getCourseTasks("token", "course-1").single() }
        assertEquals(TaskStatus.IN_PROGRESS, task.status)
    }

    private fun startServer() {
        server = HttpServer.create(InetSocketAddress(0), 0)
        server?.createContext("/") { exchange ->
            when {
                exchange.requestURI.path == "/tasks/task-sql" -> {
                    respond(
                        exchange,
                        200,
                        """{"task":{"id":"task-sql","courseId":"course-1","title":"SQL task","statementMd":"Write SQL","language":"sql","starterCode":"SELECT 1;"}}""",
                    )
                }
                exchange.requestURI.path == "/tasks/task-sql/template" -> {
                    respond(exchange, 404, """{"error":"not found"}""")
                }
                else -> {
                    respond(exchange, 404, """{"error":"unknown path"}""")
                }
            }
        }
        server?.start()
    }

    private fun startServerForCourseFlow() {
        server = HttpServer.create(InetSocketAddress(0), 0)
        server?.createContext("/") { exchange ->
            when {
                exchange.requestURI.path == "/courses/course-1" -> {
                    respond(
                        exchange,
                        200,
                        """{"course":{"id":"course-1"},"lessons":[{"id":"lesson-1","title":"Lesson One","moduleTitle":"Module A","position":1}]}""",
                    )
                }
                exchange.requestURI.path == "/lessons/lesson-1" -> {
                    respond(
                        exchange,
                        200,
                        """{"lesson":{"id":"lesson-1","title":"Lesson One","moduleTitle":"Module A","position":1},"tasks":[{"id":"task-1","title":"Task One","language":"python","type":"console"}],"blocks":[]}""",
                    )
                }
                else -> {
                    respond(exchange, 404, """{"error":"unknown path"}""")
                }
            }
        }
        server?.start()
    }

    private fun startServerForCatalogFlow() {
        server = HttpServer.create(InetSocketAddress(0), 0)
        server?.createContext("/") { exchange ->
            when {
                exchange.requestURI.path == "/courses/course-1/tasks-catalog" -> {
                    respond(
                        exchange,
                        200,
                        """{"items":[{"taskId":"task-1","lessonId":"lesson-1","lessonTitle":"Lesson One","moduleTitle":"Module A","title":"Task One","language":"python","type":"console","status":"IN_PROGRESS","locked":false,"unavailable":false}]}""",
                    )
                }
                else -> {
                    respond(exchange, 404, """{"error":"unknown path"}""")
                }
            }
        }
        server?.start()
    }

    private fun baseUrl(): String {
        val port = server?.address?.port ?: error("Server is not started")
        return "http://127.0.0.1:$port"
    }

    private fun respond(exchange: com.sun.net.httpserver.HttpExchange, status: Int, body: String) {
        exchange.sendResponseHeaders(status, body.toByteArray().size.toLong())
        exchange.responseBody.use { it.write(body.toByteArray()) }
    }
}
