package app

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func (a *App) Router() *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery(), gin.Logger(), func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", a.Cfg.FrontendURL)
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})

	r.GET("/healthz", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "service": a.Cfg.AppName})
	})

	api := r.Group("/api/v1")
	{
		api.POST("/auth/register", a.Register)
		api.POST("/auth/login", a.Login)
		api.POST("/auth/refresh", a.RefreshToken)
		api.POST("/auth/verify-email", a.VerifyEmail)
		api.POST("/auth/forgot-password", a.ForgotPassword)
		api.POST("/auth/reset-password", a.ResetPassword)

		api.POST("/payments/cardlink/webhook", a.CardlinkWebhook)
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
			authed.GET("/courses/:courseID", a.GetCourse)
			authed.GET("/lessons/:lessonID", a.GetLesson)
			authed.POST("/lessons/:lessonID/quiz-check", a.CheckLessonQuiz)
			authed.GET("/tasks/:taskID", a.GetTask)
			authed.POST("/tasks/:taskID/run", a.RunTask)
			authed.POST("/tasks/:taskID/submissions", a.CreateSubmission)
			authed.GET("/submissions/:submissionID", a.GetSubmission)
			authed.POST("/ai/task-hint", a.TaskHint)
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
