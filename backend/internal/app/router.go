package app

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func (a *App) Router() *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery(), gin.Logger(), requestIDMiddleware(), maxRequestBodyMiddleware(int64(a.Cfg.MaxRequestBodyBytes)), gzipMiddleware(), func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", a.Cfg.FrontendURL)
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
		c.Writer.Header().Set("X-Content-Type-Options", "nosniff")
		c.Writer.Header().Set("X-Frame-Options", "SAMEORIGIN")
		c.Writer.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})

	r.GET("/healthz", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": a.Cfg.AppName})
	})
	r.GET("/readyz", func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(c.Request.Context(), 2*time.Second)
		defer cancel()

		dbErr := a.DB.Ping(ctx)
		redisErr := a.Redis.Ping(ctx).Err()
		if dbErr != nil || redisErr != nil {
			if dbErr != nil {
				_ = c.Error(dbErr)
			}
			if redisErr != nil {
				_ = c.Error(redisErr)
			}
			c.JSON(http.StatusServiceUnavailable, APIError{Error: "internal server error", RequestID: requestIDFromContext(c)})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": "ready", "service": a.Cfg.AppName})
	})

	api := r.Group("/api/v1")
	{
		auth := api.Group("/auth")
		auth.Use(a.rateLimitMiddleware("auth", a.Cfg.AuthRateLimitPerMinute))
		{
			auth.POST("/register", a.Register)
			auth.POST("/login", a.Login)
			auth.POST("/refresh", a.RefreshToken)
			auth.POST("/verify-email", a.VerifyEmail)
			auth.POST("/forgot-password", a.ForgotPassword)
			auth.POST("/reset-password", a.ResetPassword)
		}

		api.POST("/payments/cardlink/webhook", a.rateLimitMiddleware("webhook", a.Cfg.WebhookRateLimitPerMinute), a.CardlinkWebhook)
		api.POST("/payments/cardlink/return/success", a.CardlinkReturnSuccess)
		api.POST("/payments/cardlink/return/fail", a.CardlinkReturnFail)
		api.GET("/payments/cardlink/return/success", a.CardlinkReturnSuccess)
		api.GET("/payments/cardlink/return/fail", a.CardlinkReturnFail)

		authed := api.Group("")
		authed.Use(a.authMiddleware())
		{
			authed.GET("/me", a.Me)
			authed.PATCH("/me/settings", a.UpdateSettings)
			authed.GET("/me/submission-history", a.SubmissionHistory)
			authed.GET("/me/achievements", a.MyAchievements)

			authed.GET("/courses", a.ListCourses)
			authed.GET("/plugin/bootstrap", a.GetPluginBootstrap)
			authed.GET("/courses/:courseID", a.GetCourse)
			authed.GET("/courses/:courseID/tasks-catalog", a.GetCourseTasksCatalog)
			authed.GET("/lessons/:lessonID", a.GetLesson)
			authed.POST("/lessons/:lessonID/blocks/:blockID/complete", a.CompleteLessonBlock)
			authed.POST("/lessons/:lessonID/quiz-check", a.CheckLessonQuiz)
			authed.GET("/tasks/:taskID", a.GetTask)
			authed.GET("/tasks/:taskID/template", a.GetTaskTemplate)
			authed.POST("/tasks/:taskID/run", a.RunTask)
			authed.POST("/tasks/:taskID/submissions", a.CreateSubmission)
			authed.POST("/tasks/:taskID/style-check", a.TaskStyleCheck)
			authed.GET("/tasks/:taskID/reference-solution", a.GetTaskReferenceSolution)
			authed.POST("/tasks/:taskID/progress/in-progress", a.MarkTaskInProgress)
			authed.POST("/tasks/:taskID/progress/reset", a.ResetTaskProgress)
			authed.GET("/submissions/:submissionID", a.GetSubmission)
			authed.POST("/sync", a.SyncTasksState)
			authed.POST("/ai/task-hint", a.rateLimitMiddleware("ai_hint", a.Cfg.AIHintRateLimitPerMinute), a.TaskHint)
			authed.GET("/leaderboard", a.Leaderboard)

			authed.GET("/plans", a.ListPlans)
			authed.GET("/subscription", a.GetSubscription)
			authed.POST("/subscription/checkout", a.CreateCheckout)
			authed.GET("/subscription/payments/:paymentID", a.GetPaymentStatus)
			authed.POST("/subscription/cancel", a.CancelSubscription)
		}

		admin := api.Group("/admin")
		admin.Use(a.authMiddleware(), adminOnly())
		{
			admin.POST("/courses", a.AdminCreateCourse)
			admin.POST("/lessons", a.AdminCreateLesson)
			admin.POST("/tasks", a.AdminCreateTask)
			admin.POST("/users/:userID/block", a.AdminBlockUser)
			admin.GET("/metrics/overview", a.AdminMetrics)
			admin.GET("/metrics/export", a.AdminMetricsExportCSV)
		}
	}

	return r
}
