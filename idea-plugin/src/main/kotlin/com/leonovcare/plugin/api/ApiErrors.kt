package com.leonovcare.plugin.api

open class ApiException(
    val statusCode: Int,
    userMessage: String,
    cause: Throwable? = null,
) : RuntimeException(userMessage, cause)

class UnauthorizedException(message: String = "Unauthorized") : ApiException(401, message)
class ForbiddenException(message: String = "Forbidden") : ApiException(403, message)
class NotFoundException(message: String = "Not found") : ApiException(404, message)
class ConflictException(message: String = "Conflict") : ApiException(409, message)
class RateLimitedException(message: String = "Too many requests") : ApiException(429, message)
class ServerErrorException(statusCode: Int, message: String = "Server error") : ApiException(statusCode, message)
class NetworkException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)
