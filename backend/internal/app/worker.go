package app

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"leonovcare/backend/internal/judge"

	"github.com/jackc/pgx/v5"
)

func (a *App) RunSubmissionWorker(ctx context.Context) error {
	a.Log.Info("submission worker started", "queue", a.Cfg.SubmissionQueueName)
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		result, err := a.Redis.BLPop(ctx, 5*time.Second, a.Cfg.SubmissionQueueName).Result()
		if err != nil {
			continue
		}
		if len(result) < 2 {
			continue
		}
		var job QueueJob
		if err := json.Unmarshal([]byte(result[1]), &job); err != nil {
			a.Log.Warn("invalid queue job", "error", err)
			continue
		}
		if err := a.processSubmissionByID(ctx, job.SubmissionID); err != nil {
			a.Log.Error("failed to process submission", "submissionId", job.SubmissionID, "error", err)
			if retryErr := a.handleSubmissionProcessingError(ctx, job.SubmissionID, err); retryErr != nil {
				a.Log.Error("failed to retry submission", "submissionId", job.SubmissionID, "error", retryErr)
			}
		}
	}
}

func (a *App) processSubmissionByID(ctx context.Context, submissionID string) error {
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin tx: %w", err)
	}
	defer tx.Rollback(ctx)

	var userID, taskID, sourceCodeRaw, status, taskLanguage, sourcePolicyRaw, solutionCode string
	err = tx.QueryRow(ctx, `
		SELECT s.user_id, s.task_id, s.source_code, s.status, COALESCE(t.language, 'java'), COALESCE(t.source_policy::text, '{}'::text), COALESCE(t.solution_code, '')
		FROM submissions s
		JOIN tasks t ON t.id = s.task_id
		WHERE s.id = $1
		FOR UPDATE
	`, submissionID).Scan(&userID, &taskID, &sourceCodeRaw, &status, &taskLanguage, &sourcePolicyRaw, &solutionCode)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil
		}
		return err
	}
	if status != "queued" {
		return nil
	}

	if _, err := tx.Exec(ctx, `
		UPDATE submissions
		SET status = 'processing',
		    processing_attempts = processing_attempts + 1,
		    updated_at = NOW()
		WHERE id = $1
	`, submissionID); err != nil {
		return fmt.Errorf("mark submission processing: %w", err)
	}

	rows, err := tx.Query(ctx, `
		SELECT input_data, expected_output
		FROM task_test_cases
		WHERE task_id = $1
		ORDER BY position ASC
	`, taskID)
	if err != nil {
		return fmt.Errorf("load test cases: %w", err)
	}
	tests := make([]judge.TestCase, 0)
	for rows.Next() {
		var input, expected string
		if err := rows.Scan(&input, &expected); err != nil {
			rows.Close()
			return err
		}
		tests = append(tests, judge.TestCase{Input: input, Expected: expected})
	}
	rows.Close()

	sourceCode, files := decodeSubmissionSourceBundle(sourceCodeRaw)
	result := a.evaluateTaskByPolicy(taskLanguage, sourceCode, files, tests, sourcePolicyRaw, solutionCode)

	if _, err := tx.Exec(ctx, `
		UPDATE submissions
		SET status = $1, score = $2, compile_output = $3, run_log = $4, feedback = $5::jsonb, updated_at = NOW()
		WHERE id = $6
	`, result.Status, result.Score, result.CompileOutput, result.RunLog, jsonMarshal(result.Tests), submissionID); err != nil {
		return fmt.Errorf("update submission: %w", err)
	}

	if result.Status == "accepted" {
		var xpReward int
		if err := tx.QueryRow(ctx, `SELECT xp_reward FROM tasks WHERE id=$1`, taskID).Scan(&xpReward); err != nil {
			return err
		}

		if _, err := tx.Exec(ctx, `
			INSERT INTO xp_events(user_id, submission_id, points, reason)
			VALUES($1, $2, $3, 'task_accepted')
			ON CONFLICT(user_id, submission_id, reason) DO NOTHING
		`, userID, submissionID, xpReward); err != nil {
			return err
		}

		if _, err := tx.Exec(ctx, `
			UPDATE users
			SET xp = xp + $1,
			    streak = streak + 1,
			    level = GREATEST(1, FLOOR(SQRT((xp + $1) / 120.0))::int + 1),
			    updated_at = NOW()
			WHERE id = $2
		`, xpReward, userID); err != nil {
			return err
		}
	} else {
		if _, err := tx.Exec(ctx, `UPDATE users SET streak = 0, updated_at = NOW() WHERE id = $1`, userID); err != nil {
			return err
		}
	}

	if err := a.applyAchievements(ctx, tx, userID); err != nil {
		return err
	}

	if err := tx.Commit(ctx); err != nil {
		return err
	}
	return nil
}

func (a *App) handleSubmissionProcessingError(ctx context.Context, submissionID string, processingErr error) error {
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	var processingAttempts int
	err = tx.QueryRow(ctx, `
		SELECT processing_attempts
		FROM submissions
		WHERE id = $1
		FOR UPDATE
	`, submissionID).Scan(&processingAttempts)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil
		}
		return err
	}

	retryLimit := a.Cfg.SubmissionMaxAttempts
	if retryLimit <= 0 {
		retryLimit = 1
	}

	runLogSuffix := fmt.Sprintf("worker error: %s", strings.TrimSpace(processingErr.Error()))

	if processingAttempts >= retryLimit {
		_, err = tx.Exec(ctx, `
			UPDATE submissions
			SET status = 'failed',
			    run_log = TRIM(BOTH E'\n' FROM CONCAT(COALESCE(run_log, ''), E'\n', $2::text)),
			    updated_at = NOW()
			WHERE id = $1
		`, submissionID, runLogSuffix)
		if err != nil {
			return err
		}
		return tx.Commit(ctx)
	}

	_, err = tx.Exec(ctx, `
		UPDATE submissions
		SET status = 'queued',
		    run_log = TRIM(BOTH E'\n' FROM CONCAT(COALESCE(run_log, ''), E'\n', $2::text)),
		    updated_at = NOW()
		WHERE id = $1
	`, submissionID, runLogSuffix)
	if err != nil {
		return err
	}
	if err := tx.Commit(ctx); err != nil {
		return err
	}

	payload := jsonMarshal(QueueJob{SubmissionID: submissionID})
	if err := a.Redis.RPush(ctx, a.Cfg.SubmissionQueueName, payload).Err(); err != nil {
		return fmt.Errorf("requeue failed: %w", err)
	}
	return nil
}

func (a *App) applyAchievements(ctx context.Context, tx pgx.Tx, userID string) error {
	var acceptedCount int
	_ = tx.QueryRow(ctx, `SELECT COUNT(*) FROM submissions WHERE user_id=$1 AND status='accepted'`, userID).Scan(&acceptedCount)
	var level int
	_ = tx.QueryRow(ctx, `SELECT level FROM users WHERE id=$1`, userID).Scan(&level)
	var streak int
	_ = tx.QueryRow(ctx, `SELECT streak FROM users WHERE id=$1`, userID).Scan(&streak)

	type unlockRule struct {
		Code      string
		Condition bool
	}
	rules := []unlockRule{
		{Code: "first_task", Condition: acceptedCount >= 1},
		{Code: "ten_clean", Condition: streak >= 10},
		{Code: "level_10", Condition: level >= 10},
	}
	for _, r := range rules {
		if !r.Condition {
			continue
		}
		_, err := tx.Exec(ctx, `
			INSERT INTO user_achievements(user_id, achievement_id)
			SELECT $1, a.id FROM achievements a WHERE a.code = $2
			ON CONFLICT(user_id, achievement_id) DO NOTHING
		`, userID, r.Code)
		if err != nil {
			return err
		}
	}
	return nil
}
