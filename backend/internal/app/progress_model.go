package app

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgtype"
)

type dbExec interface {
	Exec(ctx context.Context, sql string, arguments ...any) (pgconn.CommandTag, error)
}

type lessonProgressSnapshot struct {
	CompletedBlockIDs []string `json:"completedBlockIds"`
	CompletedBlocks   int      `json:"completedBlocks"`
	TotalBlocks       int      `json:"totalBlocks"`
	ProgressPercent   int      `json:"progressPercent"`
}

type lessonProgressRow struct {
	BlockID    string
	IsComplete bool
}

func normalizeProgressSource(raw string) string {
	switch strings.ToLower(strings.TrimSpace(raw)) {
	case "quiz":
		return "quiz"
	case "submission":
		return "submission"
	case "system":
		return "system"
	default:
		return "manual"
	}
}

func (a *App) upsertLessonBlockCompletion(
	ctx context.Context,
	exec dbExec,
	userID string,
	lessonID string,
	blockID string,
	source string,
	submissionID string,
) error {
	normalizedUserID := strings.TrimSpace(userID)
	normalizedLessonID := strings.TrimSpace(lessonID)
	normalizedBlockID := strings.TrimSpace(blockID)
	if normalizedUserID == "" || normalizedLessonID == "" || normalizedBlockID == "" {
		return fmt.Errorf("upsert lesson completion: empty user/lesson/block id")
	}

	var submission any
	if strings.TrimSpace(submissionID) != "" {
		submission = submissionID
	}

	if _, err := exec.Exec(ctx, `
		INSERT INTO user_lesson_block_progress(
			user_id,
			lesson_id,
			block_id,
			status,
			source,
			submission_id,
			completed_at,
			updated_at
		)
		VALUES($1, $2, $3, 'completed', $4, $5, NOW(), NOW())
		ON CONFLICT(user_id, block_id) DO UPDATE
		SET lesson_id = EXCLUDED.lesson_id,
		    status = 'completed',
		    source = CASE
		        WHEN user_lesson_block_progress.source = 'quiz' THEN user_lesson_block_progress.source
		        ELSE EXCLUDED.source
		    END,
		    submission_id = COALESCE(user_lesson_block_progress.submission_id, EXCLUDED.submission_id),
		    completed_at = COALESCE(user_lesson_block_progress.completed_at, EXCLUDED.completed_at, NOW()),
		    updated_at = NOW()
	`, normalizedUserID, normalizedLessonID, normalizedBlockID, normalizeProgressSource(source), submission); err != nil {
		return fmt.Errorf("upsert lesson completion: %w", err)
	}
	return nil
}

func (a *App) loadLessonProgressRows(ctx context.Context, userID, lessonID string) ([]lessonProgressRow, error) {
	rows, err := a.DB.Query(ctx, `
		SELECT
			lb.id::text,
			ulp.block_id IS NOT NULL AS is_complete
		FROM lesson_blocks lb
		LEFT JOIN user_lesson_block_progress ulp
		       ON ulp.block_id = lb.id
		      AND ulp.user_id = $2
		      AND ulp.status = 'completed'
		WHERE lb.lesson_id = $1
		  AND lb.is_published = TRUE
		ORDER BY lb.position ASC
	`, lessonID, userID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := make([]lessonProgressRow, 0)
	for rows.Next() {
		var row lessonProgressRow
		if err := rows.Scan(&row.BlockID, &row.IsComplete); err != nil {
			return nil, err
		}
		out = append(out, row)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return out, nil
}

func buildLessonProgressSnapshot(rows []lessonProgressRow) lessonProgressSnapshot {
	completedBlockIDs := make([]string, 0, len(rows))
	completedBlocks := 0
	for _, row := range rows {
		if !row.IsComplete {
			continue
		}
		completedBlocks++
		completedBlockIDs = append(completedBlockIDs, row.BlockID)
	}

	totalBlocks := len(rows)
	progressPercent := 0
	if totalBlocks > 0 {
		progressPercent = int(float64(completedBlocks*100) / float64(totalBlocks))
	}

	return lessonProgressSnapshot{
		CompletedBlockIDs: completedBlockIDs,
		CompletedBlocks:   completedBlocks,
		TotalBlocks:       totalBlocks,
		ProgressPercent:   progressPercent,
	}
}

func (a *App) loadLessonProgressSnapshot(ctx context.Context, userID, lessonID string) (lessonProgressSnapshot, error) {
	rows, err := a.loadLessonProgressRows(ctx, userID, lessonID)
	if err != nil {
		return lessonProgressSnapshot{}, err
	}
	return buildLessonProgressSnapshot(rows), nil
}

func startOfUTCDay(ts time.Time) time.Time {
	year, month, day := ts.UTC().Date()
	return time.Date(year, month, day, 0, 0, 0, 0, time.UTC)
}

func visibleStreak(rawStreak int, lastActiveDay pgtype.Date, now time.Time) int {
	if rawStreak <= 0 || !lastActiveDay.Valid {
		return 0
	}
	lastDay := startOfUTCDay(lastActiveDay.Time)
	today := startOfUTCDay(now)
	if lastDay.Before(today.AddDate(0, 0, -1)) {
		return 0
	}
	return rawStreak
}

func (a *App) applyAcceptedSubmissionStreak(ctx context.Context, tx pgx.Tx, userID string) (int, error) {
	var (
		rawStreak  int
		lastActive pgtype.Date
	)
	if err := tx.QueryRow(ctx, `
		SELECT streak, streak_last_active_day
		FROM users
		WHERE id = $1
		FOR UPDATE
	`, userID).Scan(&rawStreak, &lastActive); err != nil {
		return 0, err
	}

	today := startOfUTCDay(nowUTC())
	nextStreak := 1
	if lastActive.Valid {
		lastDay := startOfUTCDay(lastActive.Time)
		switch {
		case lastDay.Equal(today):
			nextStreak = rawStreak
			if nextStreak <= 0 {
				nextStreak = 1
			}
		case lastDay.Equal(today.AddDate(0, 0, -1)):
			nextStreak = rawStreak + 1
			if nextStreak <= 0 {
				nextStreak = 1
			}
		default:
			nextStreak = 1
		}
	}

	if _, err := tx.Exec(ctx, `
		UPDATE users
		SET streak = $1,
		    streak_last_active_day = $2::date,
		    updated_at = NOW()
		WHERE id = $3
	`, nextStreak, today.Format("2006-01-02"), userID); err != nil {
		return 0, err
	}
	return nextStreak, nil
}

func (a *App) recomputeUserStreakFromAcceptedSubmissions(ctx context.Context, tx pgx.Tx, userID string) error {
	var (
		lastAcceptedDay pgtype.Date
		rawStreak       int
	)
	if err := tx.QueryRow(ctx, `
		WITH accepted_days AS (
			SELECT (s.created_at AT TIME ZONE 'UTC')::date AS day
			FROM submissions s
			WHERE s.user_id = $1
			  AND s.status = 'accepted'
			GROUP BY (s.created_at AT TIME ZONE 'UTC')::date
		),
		ranked AS (
			SELECT day, ROW_NUMBER() OVER (ORDER BY day DESC) AS rn
			FROM accepted_days
		),
		grouped AS (
			SELECT day, (day + (rn || ' day')::interval)::date AS grp, rn
			FROM ranked
		),
		latest AS (
			SELECT day AS latest_day, grp AS latest_group
			FROM grouped
			WHERE rn = 1
		)
		SELECT
			(SELECT latest_day FROM latest),
			COALESCE((
				SELECT COUNT(*)::int
				FROM grouped g
				JOIN latest l ON l.latest_group = g.grp
			), 0) AS streak_days
	`, userID).Scan(&lastAcceptedDay, &rawStreak); err != nil {
		return err
	}

	visible := visibleStreak(rawStreak, lastAcceptedDay, nowUTC())
	if !lastAcceptedDay.Valid {
		if _, err := tx.Exec(ctx, `
			UPDATE users
			SET streak = 0,
			    streak_last_active_day = NULL,
			    updated_at = NOW()
			WHERE id = $1
		`, userID); err != nil {
			return err
		}
		return nil
	}

	if _, err := tx.Exec(ctx, `
		UPDATE users
		SET streak = $1,
		    streak_last_active_day = $2::date,
		    updated_at = NOW()
		WHERE id = $3
	`, visible, lastAcceptedDay.Time.Format("2006-01-02"), userID); err != nil {
		return err
	}
	return nil
}
