package app

import (
	"context"
	"database/sql"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
)

const (
	technicalFreePlanCode = "free"
	minimumPaidPlanCode   = "pro"
)

type courseAccessPolicy struct {
	PlanCode   string
	MaxCourses *int
}

func normalizePlanCode(raw string) string {
	if raw == "" {
		return technicalFreePlanCode
	}
	return raw
}

func (a *App) loadCourseAccessPolicy(ctx context.Context, userID string) (courseAccessPolicy, error) {
	var (
		planCode   string
		maxCourses sql.NullInt32
	)

	err := a.DB.QueryRow(ctx, `
		SELECT COALESCE(p.code, $2), p.max_courses
		FROM users u
		LEFT JOIN subscriptions s ON s.user_id = u.id
			AND s.status = 'active'
			AND (s.ends_at IS NULL OR s.ends_at > NOW())
		LEFT JOIN plans p ON p.id = s.plan_id
		WHERE u.id = $1
	`, userID, technicalFreePlanCode).Scan(&planCode, &maxCourses)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return courseAccessPolicy{}, fmt.Errorf("user %s not found", userID)
		}
		return courseAccessPolicy{}, err
	}

	out := courseAccessPolicy{
		PlanCode: normalizePlanCode(planCode),
	}
	if maxCourses.Valid {
		value := int(maxCourses.Int32)
		if value < 0 {
			value = 0
		}
		out.MaxCourses = &value
	}
	return out, nil
}

func (a *App) hasAnyCourseAccess(ctx context.Context, userID string) (bool, string, error) {
	policy, err := a.loadCourseAccessPolicy(ctx, userID)
	if err != nil {
		return false, "", err
	}
	if policy.MaxCourses == nil {
		return true, policy.PlanCode, nil
	}
	return *policy.MaxCourses > 0, policy.PlanCode, nil
}

func (a *App) canAccessCourse(ctx context.Context, userID, courseID string) (bool, string, error) {
	policy, err := a.loadCourseAccessPolicy(ctx, userID)
	if err != nil {
		return false, "", err
	}
	if policy.MaxCourses == nil {
		return true, policy.PlanCode, nil
	}
	if *policy.MaxCourses <= 0 {
		return false, policy.PlanCode, nil
	}

	var allowed bool
	if err := a.DB.QueryRow(ctx, `
		WITH ranked_courses AS (
			SELECT id, ROW_NUMBER() OVER (ORDER BY created_at ASC, id ASC) AS rn
			FROM courses
			WHERE is_published = TRUE
		)
		SELECT EXISTS(
			SELECT 1
			FROM ranked_courses
			WHERE id = $1
			  AND rn <= $2
		)
	`, courseID, *policy.MaxCourses).Scan(&allowed); err != nil {
		return false, "", err
	}
	return allowed, policy.PlanCode, nil
}
