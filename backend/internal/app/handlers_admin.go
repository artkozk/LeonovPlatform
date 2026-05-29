package app

import (
	"errors"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgconn"
)

func (a *App) AdminCreateCourse(c *gin.Context) {
	uctx, _ := userFromContext(c)
	var req struct {
		Slug        string `json:"slug" binding:"required"`
		Title       string `json:"title" binding:"required"`
		Description string `json:"description" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	var id string
	err := a.DB.QueryRow(c.Request.Context(), `
		INSERT INTO courses(slug, title, description)
		VALUES($1, $2, $3)
		RETURNING id
	`, req.Slug, req.Title, req.Description).Scan(&id)
	if err != nil {
		internalServerError(c, err)
		return
	}
	_, _ = a.DB.Exec(c.Request.Context(), `
		INSERT INTO admin_audit_log(admin_user_id, action, entity_type, entity_id, details)
		VALUES($1, 'create_course', 'course', $2, $3::jsonb)
	`, uctx.ID, id, jsonMarshal(req))
	c.JSON(http.StatusCreated, gin.H{"id": id})
}

func (a *App) AdminCreateLesson(c *gin.Context) {
	uctx, _ := userFromContext(c)
	var req struct {
		CourseID    string `json:"courseId" binding:"required,uuid"`
		ModulePos   int    `json:"modulePosition" binding:"required"`
		ModuleTitle string `json:"moduleTitle" binding:"required"`
		Title       string `json:"title" binding:"required"`
		ContentMD   string `json:"contentMd" binding:"required"`
		Position    int    `json:"position" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var moduleID string
	err = tx.QueryRow(c.Request.Context(), `
		INSERT INTO modules(course_id, title, position)
		VALUES($1, $2, $3)
		ON CONFLICT(course_id, position)
		DO UPDATE SET title = EXCLUDED.title, updated_at = NOW()
		RETURNING id
	`, req.CourseID, req.ModuleTitle, req.ModulePos).Scan(&moduleID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	var lessonID string
	err = tx.QueryRow(c.Request.Context(), `
		INSERT INTO lessons(module_id, title, content_md, position)
		VALUES($1, $2, $3, $4)
		RETURNING id
	`, moduleID, req.Title, req.ContentMD, req.Position).Scan(&lessonID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	_, _ = tx.Exec(c.Request.Context(), `
		INSERT INTO admin_audit_log(admin_user_id, action, entity_type, entity_id, details)
		VALUES($1, 'create_lesson', 'lesson', $2, $3::jsonb)
	`, uctx.ID, lessonID, jsonMarshal(req))

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusCreated, gin.H{"id": lessonID})
}

func (a *App) AdminCreateTask(c *gin.Context) {
	uctx, _ := userFromContext(c)
	var req struct {
		LessonID     string `json:"lessonId" binding:"required,uuid"`
		Title        string `json:"title" binding:"required"`
		StatementMD  string `json:"statementMd" binding:"required"`
		StarterCode  string `json:"starterCode" binding:"required"`
		SolutionCode string `json:"solutionCode" binding:"required"`
		Difficulty   int    `json:"difficulty" binding:"required,min=1,max=10"`
		XPReward     int    `json:"xpReward" binding:"required,min=10"`
		Topic        string `json:"topic" binding:"required"`
		Language     string `json:"language"`
		TestCases    []struct {
			Input    string `json:"input"`
			Expected string `json:"expected"`
			Hidden   bool   `json:"hidden"`
		} `json:"testCases" binding:"required,min=1"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	req.Language = strings.ToLower(strings.TrimSpace(req.Language))
	if req.Language == "" {
		req.Language = "java"
	}
	if req.Language != "java" && req.Language != "python" && req.Language != "sql" {
		badRequest(c, errors.New("language must be java, python or sql"))
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var taskID string
	err = tx.QueryRow(c.Request.Context(), `
		INSERT INTO tasks(lesson_id, title, statement_md, starter_code, solution_code, difficulty, xp_reward, topic, language)
		VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING id
	`, req.LessonID, req.Title, req.StatementMD, req.StarterCode, req.SolutionCode, req.Difficulty, req.XPReward, req.Topic, req.Language).Scan(&taskID)
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) && pgErr.Code == "23505" {
			c.JSON(http.StatusConflict, APIError{Error: "task with this title already exists in this lesson"})
			return
		}
		internalServerError(c, err)
		return
	}

	for i, tc := range req.TestCases {
		if _, err := tx.Exec(c.Request.Context(), `
			INSERT INTO task_test_cases(task_id, input_data, expected_output, is_hidden, position)
			VALUES($1, $2, $3, $4, $5)
		`, taskID, tc.Input, tc.Expected, tc.Hidden, i+1); err != nil {
			internalServerError(c, err)
			return
		}
	}
	_, _ = tx.Exec(c.Request.Context(), `
		INSERT INTO admin_audit_log(admin_user_id, action, entity_type, entity_id, details)
		VALUES($1, 'create_task', 'task', $2, $3::jsonb)
	`, uctx.ID, taskID, jsonMarshal(req))

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusCreated, gin.H{"id": taskID})
}

func (a *App) AdminBlockUser(c *gin.Context) {
	uctx, _ := userFromContext(c)
	userID := c.Param("userID")
	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	if _, err := tx.Exec(c.Request.Context(), `UPDATE users SET is_blocked = TRUE, updated_at = NOW() WHERE id = $1`, userID); err != nil {
		internalServerError(c, err)
		return
	}
	if _, err := tx.Exec(c.Request.Context(), `DELETE FROM refresh_tokens WHERE user_id = $1`, userID); err != nil {
		internalServerError(c, err)
		return
	}
	_, _ = tx.Exec(c.Request.Context(), `
		INSERT INTO admin_audit_log(admin_user_id, action, entity_type, entity_id)
		VALUES($1, 'block_user', 'user', $2)
	`, uctx.ID, userID)
	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "blocked"})
}

func (a *App) AdminMetrics(c *gin.Context) {
	var users, activePaidSubs, submissions24h, accepted24h int
	_ = a.DB.QueryRow(c.Request.Context(), `SELECT COUNT(*) FROM users`).Scan(&users)
	_ = a.DB.QueryRow(c.Request.Context(), `
		SELECT COUNT(*)
		FROM subscriptions s
		JOIN plans p ON p.id = s.plan_id
		WHERE s.status='active'
		  AND (s.ends_at IS NULL OR s.ends_at > NOW())
		  AND p.code <> $1
	`, technicalFreePlanCode).Scan(&activePaidSubs)
	_ = a.DB.QueryRow(c.Request.Context(), `SELECT COUNT(*) FROM submissions WHERE created_at >= NOW() - interval '24 hour'`).Scan(&submissions24h)
	_ = a.DB.QueryRow(c.Request.Context(), `SELECT COUNT(*) FROM submissions WHERE status='accepted' AND created_at >= NOW() - interval '24 hour'`).Scan(&accepted24h)

	conversion := 0.0
	if users > 0 {
		conversion = float64(activePaidSubs) / float64(users) * 100
	}

	c.JSON(http.StatusOK, gin.H{
		"usersTotal":              users,
		"activePaidSubscriptions": activePaidSubs,
		"submissionsLast24h":      submissions24h,
		"acceptedLast24h":         accepted24h,
		"conversionToPaidPercent": conversion,
		"generatedAt":             time.Now().UTC(),
	})
}
