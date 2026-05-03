package app

import (
	"net/http"
	"strings"

	"leonovcare/backend/internal/security"

	"github.com/gin-gonic/gin"
)

const userContextKey = "user_ctx"

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
		if err := a.DB.QueryRow(c.Request.Context(), `
			SELECT COALESCE(p.code, 'free')
			FROM users u
			LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active' AND (s.ends_at IS NULL OR s.ends_at > NOW())
			LEFT JOIN plans p ON p.id = s.plan_id
			WHERE u.id = $1
		`, claims.UserID).Scan(&ctx.PlanCode); err != nil {
			ctx.PlanCode = "free"
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
