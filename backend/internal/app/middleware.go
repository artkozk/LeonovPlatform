package app

import (
	"compress/gzip"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"leonovcare/backend/internal/security"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const userContextKey = "user_ctx"

func requestIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := strings.TrimSpace(c.GetHeader("X-Request-Id"))
		if requestID == "" {
			requestID = uuid.NewString()
		}
		c.Set(requestIDContextKey, requestID)
		c.Writer.Header().Set("X-Request-Id", requestID)
		c.Next()
	}
}

type gzipResponseWriter struct {
	gin.ResponseWriter
	writer io.Writer
}

func (g *gzipResponseWriter) Write(data []byte) (int, error) {
	return g.writer.Write(data)
}

func (g *gzipResponseWriter) WriteString(s string) (int, error) {
	return g.writer.Write([]byte(s))
}

func gzipMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if strings.Contains(strings.ToLower(c.GetHeader("Connection")), "upgrade") {
			c.Next()
			return
		}
		if !strings.Contains(strings.ToLower(c.GetHeader("Accept-Encoding")), "gzip") {
			c.Next()
			return
		}

		gz := gzip.NewWriter(c.Writer)
		defer gz.Close()

		c.Header("Content-Encoding", "gzip")
		c.Header("Vary", "Accept-Encoding")
		c.Header("Content-Length", "")

		c.Writer = &gzipResponseWriter{
			ResponseWriter: c.Writer,
			writer:         gz,
		}
		c.Next()
	}
}

func maxRequestBodyMiddleware(maxBytes int64) gin.HandlerFunc {
	return func(c *gin.Context) {
		if maxBytes > 0 && c.Request != nil && c.Request.Body != nil {
			c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxBytes)
		}
		c.Next()
	}
}

func clientKeyForRateLimit(c *gin.Context) string {
	if uctx, ok := userFromContext(c); ok && strings.TrimSpace(uctx.ID) != "" {
		return "user:" + uctx.ID
	}
	clientIP := strings.TrimSpace(c.ClientIP())
	if clientIP == "" {
		clientIP = "unknown"
	}
	return "ip:" + clientIP
}

func (a *App) rateLimitMiddleware(scope string, limitPerMinute int) gin.HandlerFunc {
	return func(c *gin.Context) {
		if limitPerMinute <= 0 {
			c.Next()
			return
		}
		minuteBucket := time.Now().UTC().Format("200601021504")
		key := fmt.Sprintf("rate_limit:%s:%s:%s", strings.TrimSpace(scope), clientKeyForRateLimit(c), minuteBucket)
		count, err := a.Redis.Incr(c.Request.Context(), key).Result()
		if err != nil {
			_ = c.Error(fmt.Errorf("rate limit redis failure: %w", err))
			c.Next()
			return
		}
		if count == 1 {
			_ = a.Redis.Expire(c.Request.Context(), key, 2*time.Minute).Err()
		}
		if count > int64(limitPerMinute) {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, APIError{Error: "rate limit exceeded"})
			return
		}
		c.Next()
	}
}

func (a *App) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "missing authorization header"})
			return
		}
		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "invalid authorization header"})
			return
		}

		claims, err := security.ParseToken(parts[1], a.Cfg.JWTAccessSecret)
		if err != nil || claims.Type != "access" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, APIError{Error: "invalid access token"})
			return
		}

		if err := a.ensureSubscriptionState(c.Request.Context(), claims.UserID); err != nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, APIError{Error: "failed to resolve subscription state"})
			return
		}

		ctx := UserContext{ID: claims.UserID, Role: claims.Role}
		var isBlocked bool
		if err := a.DB.QueryRow(c.Request.Context(), `
			SELECT u.is_blocked, COALESCE(p.code, 'free')
			FROM users u
			LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active' AND (s.ends_at IS NULL OR s.ends_at > NOW())
			LEFT JOIN plans p ON p.id = s.plan_id
			WHERE u.id = $1
		`, claims.UserID).Scan(&isBlocked, &ctx.PlanCode); err != nil {
			ctx.PlanCode = "free"
		}
		if isBlocked {
			c.AbortWithStatusJSON(http.StatusForbidden, APIError{Error: "account blocked"})
			return
		}

		c.Set(userContextKey, ctx)
		c.Next()
	}
}

func userFromContext(c *gin.Context) (UserContext, bool) {
	v, ok := c.Get(userContextKey)
	if !ok {
		return UserContext{}, false
	}
	ctx, ok := v.(UserContext)
	return ctx, ok
}

func adminOnly() gin.HandlerFunc {
	return func(c *gin.Context) {
		uctx, ok := userFromContext(c)
		if !ok || uctx.Role != "admin" {
			c.AbortWithStatusJSON(http.StatusForbidden, APIError{Error: "admin access required"})
			return
		}
		c.Next()
	}
}
