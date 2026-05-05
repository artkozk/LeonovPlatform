package app

import (
	"fmt"
	"net/http"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

func (a *App) GetTaskTemplate(c *gin.Context) {
	if _, ok := userFromContext(c); !ok {
		unauthorized(c, "unauthorized")
		return
	}

	taskID := c.Param("taskID")
	var title, language, sourcePolicyRaw, statementMD, starterCode, solutionCode string
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT
			COALESCE(title, ''),
			COALESCE(language, 'java'),
			COALESCE(source_policy::text, '{}'::text),
			COALESCE(statement_md, ''),
			COALESCE(starter_code, ''),
			COALESCE(solution_code, '')
		FROM tasks
		WHERE id = $1 AND is_published = TRUE
	`, taskID).Scan(&title, &language, &sourcePolicyRaw, &statementMD, &starterCode, &solutionCode); err != nil {
		notFound(c, "task not found")
		return
	}

	mainPath := inferMainFilePathFromSourcePolicy(sourcePolicyRaw, language)
	starter := withStarterFallback(starterCode, statementMD, language, solutionCode)
	files := buildTemplateFilesFromSourcePolicy(sourcePolicyRaw, language, title, mainPath, starter)

	c.JSON(http.StatusOK, gin.H{
		"taskId": taskID,
		"files":  files,
	})
}

func buildTemplateFilesFromSourcePolicy(sourcePolicyRaw, language, title, mainPath, starter string) []gin.H {
	paths := inferTemplateFilesFromSourcePolicy(sourcePolicyRaw, language)
	if len(paths) == 0 {
		paths = []string{mainPath}
	}
	files := make([]gin.H, 0, len(paths))
	mainNormalized := strings.ToLower(filepath.ToSlash(strings.TrimSpace(mainPath)))
	for _, path := range paths {
		normalized := filepath.ToSlash(strings.TrimSpace(path))
		if normalized == "" {
			continue
		}
		content := ""
		if strings.ToLower(normalized) == mainNormalized {
			content = starter
		} else if strings.EqualFold(filepath.Base(normalized), "README.md") {
			content = defaultReadmeTemplate(title, mainPath)
		}
		files = append(files, gin.H{
			"path":     normalized,
			"content":  content,
			"editable": true,
		})
	}
	if len(files) == 0 {
		files = append(files, gin.H{
			"path":     mainPath,
			"content":  starter,
			"editable": true,
		})
	}
	return files
}

func defaultReadmeTemplate(taskTitle, mainPath string) string {
	title := strings.TrimSpace(taskTitle)
	if title == "" {
		title = "Решение задачи"
	}
	entry := strings.TrimSpace(mainPath)
	if entry == "" {
		entry = "main.py"
	}
	content := fmt.Sprintf(
		"# %s\n\n## Запуск\n\n```bash\npython %s\n```\n\n## Пример\n\nВвод:\n\n```text\n2026\n```\n\nВывод:\n\n```text\n2027\n```\n",
		title,
		entry,
	)
	return strings.TrimSpace(content) + "\n"
}

func (a *App) TaskStyleCheck(c *gin.Context) {
	if _, ok := userFromContext(c); !ok {
		unauthorized(c, "unauthorized")
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"items": []gin.H{},
	})
}

func (a *App) GetTaskReferenceSolution(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	taskID := c.Param("taskID")
	var language, sourcePolicyRaw, solutionCode string
	if err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(language, 'java'), COALESCE(source_policy::text, '{}'::text), COALESCE(solution_code, '')
		FROM tasks
		WHERE id = $1 AND is_published = TRUE
	`, taskID).Scan(&language, &sourcePolicyRaw, &solutionCode); err != nil {
		notFound(c, "task not found")
		return
	}

	if strings.TrimSpace(solutionCode) == "" {
		c.JSON(http.StatusOK, gin.H{
			"taskId":            taskID,
			"available":         false,
			"unavailableReason": "Reference solution is unavailable",
			"files":             []gin.H{},
		})
		return
	}

	if uctx.Role != "admin" {
		var solvedCount int
		if err := a.DB.QueryRow(c.Request.Context(), `
			SELECT COUNT(*)
			FROM submissions
			WHERE user_id = $1 AND task_id = $2 AND status = 'accepted'
		`, uctx.ID, taskID).Scan(&solvedCount); err != nil {
			internalServerError(c, err)
			return
		}
		if solvedCount == 0 {
			c.JSON(http.StatusForbidden, APIError{Error: "reference solution is available after accepted submission"})
			return
		}
	}

	mainPath := inferMainFilePathFromSourcePolicy(sourcePolicyRaw, language)
	c.JSON(http.StatusOK, gin.H{
		"taskId":    taskID,
		"available": true,
		"files": []gin.H{
			{
				"path":    mainPath,
				"content": strings.TrimSpace(solutionCode),
			},
		},
	})
}

func (a *App) ResetTaskProgress(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	taskID := c.Param("taskID")

	ctx := c.Request.Context()
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(ctx)

	var exists bool
	if err := tx.QueryRow(ctx, `
		SELECT EXISTS(SELECT 1 FROM tasks WHERE id = $1 AND is_published = TRUE)
	`, taskID).Scan(&exists); err != nil {
		internalServerError(c, err)
		return
	}
	if !exists {
		notFound(c, "task not found")
		return
	}

	xpTag, err := tx.Exec(ctx, `
		DELETE FROM xp_events
		WHERE user_id = $1
		  AND submission_id IN (
			SELECT id
			FROM submissions
			WHERE user_id = $1 AND task_id = $2
		  )
	`, uctx.ID, taskID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	submissionsTag, err := tx.Exec(ctx, `
		DELETE FROM submissions
		WHERE user_id = $1 AND task_id = $2
	`, uctx.ID, taskID)
	if err != nil {
		internalServerError(c, err)
		return
	}

	var xp int
	if err := tx.QueryRow(ctx, `
		SELECT COALESCE(SUM(points), 0)
		FROM xp_events
		WHERE user_id = $1
	`, uctx.ID).Scan(&xp); err != nil {
		internalServerError(c, err)
		return
	}

	var level int
	if err := tx.QueryRow(ctx, `
		SELECT GREATEST(1, FLOOR(SQRT($1 / 120.0))::int + 1)
	`, xp).Scan(&level); err != nil {
		internalServerError(c, err)
		return
	}

	if _, err := tx.Exec(ctx, `
		UPDATE users
		SET xp = $1,
		    level = $2,
		    streak = 0,
		    updated_at = NOW()
		WHERE id = $3
	`, xp, level, uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(ctx); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":             "reset",
		"removedSubmissions": submissionsTag.RowsAffected(),
		"removedXPEvents":    xpTag.RowsAffected(),
	})
}

func (a *App) SyncTasksState(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	ctx := c.Request.Context()
	var updatedTasks int
	if err := a.DB.QueryRow(ctx, `
		SELECT COUNT(*)
		FROM tasks t
		JOIN lessons l ON l.id = t.lesson_id
		JOIN modules m ON m.id = l.module_id
		JOIN courses crs ON crs.id = m.course_id
		WHERE t.is_published = TRUE
		  AND l.is_published = TRUE
		  AND crs.is_published = TRUE
	`).Scan(&updatedTasks); err != nil {
		internalServerError(c, err)
		return
	}

	var changedStatuses int
	if err := a.DB.QueryRow(ctx, `
		SELECT COUNT(*)
		FROM submissions
		WHERE user_id = $1
		  AND updated_at >= NOW() - INTERVAL '24 hours'
	`, uctx.ID).Scan(&changedStatuses); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"updatedTasks":    updatedTasks,
		"changedStatuses": changedStatuses,
		"unlockedTasks":   0,
		"serverTime":      nowUTC(),
		"errors":          []string{},
	})
}
