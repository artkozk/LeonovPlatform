package com.leonovcare.plugin.api

import com.sun.net.httpserver.HttpServer
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

    private fun baseUrl(): String {
        val port = server?.address?.port ?: error("Server is not started")
        return "http://127.0.0.1:$port"
    }

    private fun respond(exchange: com.sun.net.httpserver.HttpExchange, status: Int, body: String) {
        exchange.sendResponseHeaders(status, body.toByteArray().size.toLong())
        exchange.responseBody.use { it.write(body.toByteArray()) }
    }
}
