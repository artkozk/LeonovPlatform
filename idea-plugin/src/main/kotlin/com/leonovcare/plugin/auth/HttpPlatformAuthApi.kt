package com.leonovcare.plugin.auth

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.leonovcare.plugin.api.ApiException
import com.leonovcare.plugin.api.ConflictException
import com.leonovcare.plugin.api.ForbiddenException
import com.leonovcare.plugin.api.NetworkException
import com.leonovcare.plugin.api.NotFoundException
import com.leonovcare.plugin.api.RateLimitedException
import com.leonovcare.plugin.api.ServerErrorException
import com.leonovcare.plugin.api.UnauthorizedException
import com.leonovcare.plugin.settings.PlatformSettings
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration

class HttpPlatformAuthApi(
    private val settings: PlatformSettings = PlatformSettings.getInstance(),
    private val timeout: Duration = Duration.ofSeconds(20),
) : PlatformAuthApi {

    private val mapper = ObjectMapper()
        .registerModule(KotlinModule.Builder().build())
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)

    private val httpClient = HttpClient.newBuilder().build()

    override suspend fun login(email: String, password: String): AuthTokens {
        val payload = mapper.writeValueAsString(
            mapOf(
                "email" to email,
                "password" to password,
            )
        )
        val node = requestNode(path = "/auth/login", payload = payload)
        return parseTokens(node)
    }

    override suspend fun refresh(refreshToken: String): AuthTokens {
        val payload = mapper.writeValueAsString(
            mapOf(
                "refreshToken" to refreshToken,
            )
        )
        val node = requestNode(path = "/auth/refresh", payload = payload)
        return parseTokens(node)
    }

    private suspend fun requestNode(path: String, payload: String): JsonNode {
        return withContext(Dispatchers.IO) {
            val url = buildUrl(path)
            try {
                val request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .timeout(timeout)
                    .header("Accept", "application/json")
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(payload))
                    .build()

                val response = httpClient.send(request, HttpResponse.BodyHandlers.ofString())
                val status = response.statusCode()
                val body = response.body().orEmpty()

                if (status in 200..299) {
                    return@withContext if (body.isBlank()) mapper.createObjectNode() else mapper.readTree(body)
                }

                throw toApiException(status, body)
            } catch (apiException: ApiException) {
                throw apiException
            } catch (ex: Exception) {
                throw NetworkException("Auth request failed: POST $path", ex)
            }
        }
    }

    private fun parseTokens(node: JsonNode): AuthTokens {
        val directAccess = node.path("accessToken").asText("").trim()
        val directRefresh = node.path("refreshToken").asText("").trim()
        val nested = node.path("tokens")
        val nestedAccess = nested.path("accessToken").asText("").trim()
        val nestedRefresh = nested.path("refreshToken").asText("").trim()

        val access = if (directAccess.isNotBlank()) directAccess else nestedAccess
        val refresh = if (directRefresh.isNotBlank()) directRefresh else nestedRefresh

        if (access.isBlank()) {
            throw ApiException(500, "Auth response does not contain access token")
        }

        return AuthTokens(
            accessToken = access,
            refreshToken = refresh.ifBlank { null },
        )
    }

    private fun toApiException(status: Int, body: String): ApiException {
        val message = parseErrorMessage(body)
        return when (status) {
            401 -> UnauthorizedException(message)
            403 -> ForbiddenException(message)
            404 -> NotFoundException(message)
            409 -> ConflictException(message)
            429 -> RateLimitedException(message)
            in 500..599 -> ServerErrorException(status, message)
            else -> ApiException(status, message)
        }
    }

    private fun parseErrorMessage(body: String): String {
        if (body.isBlank()) return "Unexpected auth error"
        return runCatching {
            val json = mapper.readTree(body)
            json.path("error").asText().ifBlank {
                json.path("details").asText().ifBlank { json.path("message").asText() }
            }
        }.getOrDefault(body)
    }

    private fun buildUrl(path: String): String {
        val baseUrl = settings.mutableState().apiBaseUrl.trimEnd('/')
        return baseUrl + if (path.startsWith('/')) path else "/$path"
    }
}
