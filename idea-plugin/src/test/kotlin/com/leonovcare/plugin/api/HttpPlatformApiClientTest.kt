package com.leonovcare.plugin.api

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import java.net.InetSocketAddress
import java.nio.charset.StandardCharsets

class HttpPlatformApiClientTest {

    private var server: HttpServer? = null

    @AfterEach
    fun tearDown() {
        server?.stop(0)
        server = null
    }

    @Test
    fun `maps 401 to UnauthorizedException`() {
        startServer { exchange ->
            respond(exchange, 401, "{\"error\":\"invalid token\"}")
        }

        val client = HttpPlatformApiClient(baseUrl())

        assertThrows(UnauthorizedException::class.java) {
            runBlocking { client.getCurrentUser("token") }
        }
    }

    @Test
    fun `maps 500 to ServerErrorException`() {
        startServer { exchange ->
            respond(exchange, 500, "{\"error\":\"boom\"}")
        }

        val client = HttpPlatformApiClient(baseUrl())

        assertThrows(ServerErrorException::class.java) {
            runBlocking { client.getCourses("token") }
        }
    }

    @Test
    fun `reference solution 403 returns unavailable`() {
        startServer { exchange ->
            respond(exchange, 403, "{\"error\":\"forbidden\"}")
        }

        val client = HttpPlatformApiClient(baseUrl())
        val solution = runBlocking { client.getReferenceSolution("token", "task-1") }

        assertFalse(solution.available)
        assertEquals("task-1", solution.taskId)
    }

    @Test
    fun `requests ai hint and maps response`() {
        startServer { exchange ->
            assertEquals("/ai/task-hint", exchange.requestURI.path)
            val body = String(exchange.requestBody.readAllBytes(), StandardCharsets.UTF_8)
            assertTrue(body.contains("\"taskId\":\"task-1\""))
            assertTrue(body.contains("\"sourceCode\":\"print(1)\""))
            respond(
                exchange,
                200,
                """{"status":"ok","hint":"step","model":"gpt","usage":{"promptTokens":10,"completionTokens":20,"totalTokens":30}}""",
            )
        }

        val client = HttpPlatformApiClient(baseUrl())
        val hint = runBlocking { client.requestAiHint("token", "task-1", "print(1)") }

        requireNotNull(hint)
        assertEquals("ok", hint.status)
        assertEquals("step", hint.hint)
        assertEquals("gpt", hint.model)
        assertEquals(30, hint.usage?.totalTokens)
    }

    @Test
    fun `returns null ai hint when endpoint is not implemented`() {
        startServer { exchange ->
            respond(exchange, 404, "{\"error\":\"not found\"}")
        }

        val client = HttpPlatformApiClient(baseUrl())
        val hint = runBlocking { client.requestAiHint("token", "task-1", "print(1)") }
        assertNull(hint)
    }

    private fun startServer(handler: (HttpExchange) -> Unit) {
        server = HttpServer.create(InetSocketAddress(0), 0)
        server?.createContext("/") { exchange -> handler(exchange) }
        server?.start()
    }

    private fun baseUrl(): String {
        val port = server?.address?.port ?: error("Server is not started")
        return "http://127.0.0.1:$port"
    }

    private fun respond(exchange: HttpExchange, status: Int, body: String) {
        exchange.sendResponseHeaders(status, body.toByteArray().size.toLong())
        exchange.responseBody.use { it.write(body.toByteArray()) }
    }
}
