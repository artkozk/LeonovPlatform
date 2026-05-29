package app

import (
	"errors"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5"
)

func writeSubscriptionRequiredResponse(c *gin.Context, planCode string) {
	currentPlan := strings.TrimSpace(planCode)
	if currentPlan == "" {
		currentPlan = technicalFreePlanCode
	}
	c.JSON(http.StatusPaymentRequired, gin.H{
		"error":        "active subscription required for course access",
		"status":       "subscription_required",
		"requiredPlan": minimumPaidPlanCode,
		"currentPlan":  currentPlan,
	})
}

func writeCourseLimitResponse(c *gin.Context, planCode string) {
	currentPlan := strings.TrimSpace(planCode)
	if currentPlan == "" {
		currentPlan = technicalFreePlanCode
	}
	requiredPlan := minimumPaidPlanCode
	if currentPlan == minimumPaidPlanCode {
		requiredPlan = "premium"
	}
	c.JSON(http.StatusPaymentRequired, gin.H{
		"error":        "current plan does not include this course",
		"status":       "course_not_in_plan",
		"requiredPlan": requiredPlan,
		"currentPlan":  currentPlan,
	})
}

func (a *App) requireAnyCourseAccess(c *gin.Context, userID string) bool {
	allowed, planCode, err := a.hasAnyCourseAccess(c.Request.Context(), userID)
	if err != nil {
		internalServerError(c, err)
		return false
	}
	if !allowed {
		writeSubscriptionRequiredResponse(c, planCode)
		return false
	}
	return true
}

func (a *App) requireCourseAccess(c *gin.Context, userID, courseID string) bool {
	allowed, planCode, err := a.canAccessCourse(c.Request.Context(), userID, courseID)
	if err != nil {
		internalServerError(c, err)
		return false
	}
	if !allowed {
		if strings.EqualFold(planCode, technicalFreePlanCode) {
			writeSubscriptionRequiredResponse(c, planCode)
			return false
		}
		writeCourseLimitResponse(c, planCode)
		return false
	}
	return true
}

func (a *App) resolveCourseIDByLesson(c *gin.Context, lessonID string) (string, bool) {
	var courseID string
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT m.course_id
		FROM lessons l
		JOIN modules m ON m.id = l.module_id
		JOIN courses c ON c.id = m.course_id
		WHERE l.id = $1
		  AND l.is_published = TRUE
		  AND c.is_published = TRUE
		LIMIT 1
	`, lessonID).Scan(&courseID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			notFound(c, "lesson not found")
			return "", false
		}
		internalServerError(c, err)
		return "", false
	}
	return courseID, true
}

func (a *App) resolveCourseIDByTask(c *gin.Context, taskID string) (string, bool) {
	var courseID string
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT m.course_id
		FROM tasks t
		JOIN lessons l ON l.id = t.lesson_id
		JOIN modules m ON m.id = l.module_id
		JOIN courses c ON c.id = m.course_id
		WHERE t.id = $1
		  AND t.is_published = TRUE
		  AND l.is_published = TRUE
		  AND c.is_published = TRUE
		LIMIT 1
	`, taskID).Scan(&courseID)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			notFound(c, "task not found")
			return "", false
		}
		internalServerError(c, err)
		return "", false
	}
	return courseID, true
}
