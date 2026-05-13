package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"leonovcare/backend/internal/judge"

	"github.com/jackc/pgx/v5"
	"github.com/redis/go-redis/v9"
)

type claimedSubmission struct {
	SubmissionID    string
	UserID          string
	TaskID          string
	SourceCodeRaw   string
	TaskLanguage    string
	SourcePolicyRaw string
	SolutionCode    string
}

func (a *App) RunSubmissionWorker(ctx context.Context) error {
	mainQueue := strings.TrimSpace(a.Cfg.SubmissionQueueName)
	processingQueue := strings.TrimSpace(a.Cfg.SubmissionProcessingQueueName)
	if mainQueue == "" {
		mainQueue = "submission_jobs"
	}
	if processingQueue == "" {
		processingQueue = mainQueue + "_processing"
	}

	a.Log.Info("submission worker started", "queue", mainQueue, "processingQueue", processingQueue)
	go a.runSubmissionQueueReconciler(ctx, mainQueue, processingQueue)

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		payload, err := a.Redis.BRPopLPush(ctx, mainQueue, processingQueue, 5*time.Second).Result()
		if err != nil {
			if err == redis.Nil {
				continue
			}
			if ctx.Err() != nil {
				return ctx.Err()
			}
			a.Log.Warn("failed to pop submission job", "error", err)
			continue
		}
		payload = strings.TrimSpace(payload)
		if payload == "" {
			continue
		}

		var job QueueJob
		if err := json.Unmarshal([]byte(payload), &job); err != nil {
			a.Log.Warn("invalid queue job", "payload", payload, "error", err)
			if ackErr := a.ackSubmissionProcessingPayload(ctx, processingQueue, payload); ackErr != nil {
				a.Log.Error("failed to ack broken queue payload", "error", ackErr)
			}
			continue
		}

		processErr := a.processSubmissionByID(ctx, job.SubmissionID)
		if processErr != nil {
			a.Log.Error("failed to process submission", "submissionId", job.SubmissionID, "error", processErr)
			if retryErr := a.handleSubmissionProcessingError(ctx, job.SubmissionID, processErr); retryErr != nil {
				a.Log.Error("failed to retry submission", "submissionId", job.SubmissionID, "error", retryErr)
			}
		}

		if ackErr := a.ackSubmissionProcessingPayload(ctx, processingQueue, payload); ackErr != nil {
			a.Log.Error("failed to ack processed queue job", "submissionId", job.SubmissionID, "error", ackErr)
		}
	}
}

func (a *App) ackSubmissionProcessingPayload(ctx context.Context, processingQueue, payload string) error {
	removed, err := a.Redis.LRem(ctx, processingQueue, 1, payload).Result()
	if err != nil {
		return err
	}
	if removed == 0 {
		a.Log.Warn("processing payload was not found during ack", "queue", processingQueue)
	}
	return nil
}

func (a *App) runSubmissionQueueReconciler(ctx context.Context, queue, processingQueue string) {
	interval := a.Cfg.SubmissionReconcileInterval
	if interval <= 0 {
		interval = 30 * time.Second
	}
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := a.reconcileQueuedSubmissions(ctx, queue, processingQueue); err != nil && ctx.Err() == nil {
				a.Log.Warn("submission queue reconciler failed", "error", err)
			}
		}
	}
}

func (a *App) reconcileQueuedSubmissions(ctx context.Context, queue, processingQueue string) error {
	limit := a.Cfg.SubmissionReconcileBatch
	if limit <= 0 {
		limit = 200
	}

	rows, err := a.DB.Query(ctx, `
		SELECT id
		FROM submissions
		WHERE status = 'queued'
		ORDER BY updated_at ASC, created_at ASC
		LIMIT $1
	`, limit)
	if err != nil {
		return fmt.Errorf("load queued submissions for reconcile: %w", err)
	}
	defer rows.Close()

	jobs := make([]string, 0, limit)
	for rows.Next() {
		var submissionID string
		if err := rows.Scan(&submissionID); err != nil {
			return err
		}
		jobs = append(jobs, jsonMarshal(QueueJob{SubmissionID: submissionID}))
	}
	if err := rows.Err(); err != nil {
		return err
	}
	if len(jobs) == 0 {
		return nil
	}

	values := make([]interface{}, 0, len(jobs))
	for _, payload := range jobs {
		inMainQueue, err := a.submissionQueueContainsPayload(ctx, queue, payload)
		if err != nil {
			return fmt.Errorf("check queue payload in main queue: %w", err)
		}
		if inMainQueue {
			continue
		}

		inProcessingQueue, err := a.submissionQueueContainsPayload(ctx, processingQueue, payload)
		if err != nil {
			return fmt.Errorf("check queue payload in processing queue: %w", err)
		}
		if inProcessingQueue {
			continue
		}

		values = append(values, payload)
	}
	if len(values) == 0 {
		return nil
	}
	if err := a.Redis.RPush(ctx, queue, values...).Err(); err != nil {
		return fmt.Errorf("requeue queued submissions: %w", err)
	}
	return nil
}

func (a *App) submissionQueueContainsPayload(ctx context.Context, queue, payload string) (bool, error) {
	_, err := a.Redis.LPos(ctx, queue, payload, redis.LPosArgs{}).Result()
	if err == nil {
		return true, nil
	}
	if errors.Is(err, redis.Nil) {
		return false, nil
	}
	return false, err
}

func (a *App) processSubmissionByID(ctx context.Context, submissionID string) error {
	claimed, err := a.claimSubmissionForProcessing(ctx, submissionID)
	if err != nil {
		return err
	}
	if claimed == nil {
		return nil
	}

	tests, err := a.loadTaskTestCases(ctx, claimed.TaskID)
	if err != nil {
		return err
	}

	sourceCode, files := decodeSubmissionSourceBundle(claimed.SourceCodeRaw)
	result := a.evaluateTaskByPolicy(claimed.TaskLanguage, sourceCode, files, tests, claimed.SourcePolicyRaw, claimed.SolutionCode)

	if err := a.finalizeSubmissionResult(ctx, claimed, result); err != nil {
		return err
	}
	return nil
}

func (a *App) claimSubmissionForProcessing(ctx context.Context, submissionID string) (*claimedSubmission, error) {
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return nil, fmt.Errorf("begin tx: %w", err)
	}
	defer tx.Rollback(ctx)

	var claimed claimedSubmission
	var status string
	err = tx.QueryRow(ctx, `
		SELECT s.id, s.user_id, s.task_id, s.source_code, s.status,
		       COALESCE(t.language, 'java'), COALESCE(t.source_policy::text, '{}'::text), COALESCE(t.solution_code, '')
		FROM submissions s
		JOIN tasks t ON t.id = s.task_id
		WHERE s.id = $1
		FOR UPDATE
	`, submissionID).Scan(
		&claimed.SubmissionID,
		&claimed.UserID,
		&claimed.TaskID,
		&claimed.SourceCodeRaw,
		&status,
		&claimed.TaskLanguage,
		&claimed.SourcePolicyRaw,
		&claimed.SolutionCode,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	if status != "queued" {
		return nil, nil
	}

	if _, err := tx.Exec(ctx, `
		UPDATE submissions
		SET status = 'processing',
		    processing_attempts = processing_attempts + 1,
		    updated_at = NOW()
		WHERE id = $1
	`, submissionID); err != nil {
		return nil, fmt.Errorf("mark submission processing: %w", err)
	}

	if err := tx.Commit(ctx); err != nil {
		return nil, err
	}
	return &claimed, nil
}

func (a *App) loadTaskTestCases(ctx context.Context, taskID string) ([]judge.TestCase, error) {
	rows, err := a.DB.Query(ctx, `
		SELECT input_data, expected_output
		FROM task_test_cases
		WHERE task_id = $1
		ORDER BY position ASC
	`, taskID)
	if err != nil {
		return nil, fmt.Errorf("load test cases: %w", err)
	}
	defer rows.Close()

	tests := make([]judge.TestCase, 0)
	for rows.Next() {
		var input, expected string
		if err := rows.Scan(&input, &expected); err != nil {
			return nil, err
		}
		tests = append(tests, judge.TestCase{Input: input, Expected: expected})
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return tests, nil
}

func (a *App) finalizeSubmissionResult(ctx context.Context, claimed *claimedSubmission, result judge.Result) error {
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return fmt.Errorf("begin finalize tx: %w", err)
	}
	defer tx.Rollback(ctx)

	commandTag, err := tx.Exec(ctx, `
		UPDATE submissions
		SET status = $1,
		    score = $2,
		    compile_output = $3,
		    run_log = $4,
		    feedback = $5::jsonb,
		    updated_at = NOW()
		WHERE id = $6 AND status = 'processing'
	`, result.Status, result.Score, result.CompileOutput, result.RunLog, jsonMarshal(result.Tests), claimed.SubmissionID)
	if err != nil {
		return fmt.Errorf("update submission: %w", err)
	}
	if commandTag.RowsAffected() == 0 {
		return nil
	}

	if result.Status == "accepted" {
		var xpReward int
		if err := tx.QueryRow(ctx, `SELECT xp_reward FROM tasks WHERE id=$1`, claimed.TaskID).Scan(&xpReward); err != nil {
			return err
		}

		xpInsertTag, err := tx.Exec(ctx, `
			INSERT INTO xp_events(user_id, submission_id, points, reason)
			VALUES($1, $2, $3, 'task_accepted')
			ON CONFLICT(user_id, submission_id, reason) DO NOTHING
		`, claimed.UserID, claimed.SubmissionID, xpReward)
		if err != nil {
			return err
		}

		if xpInsertTag.RowsAffected() > 0 {
			if _, err := tx.Exec(ctx, `
				UPDATE users
				SET xp = xp + $1,
				    level = GREATEST(1, FLOOR(SQRT((xp + $1) / 120.0))::int + 1),
				    updated_at = NOW()
				WHERE id = $2
			`, xpReward, claimed.UserID); err != nil {
				return err
			}
		}

		if _, err := a.applyAcceptedSubmissionStreak(ctx, tx, claimed.UserID); err != nil {
			return err
		}

		var (
			lessonID string
			blockID  string
		)
		err = tx.QueryRow(ctx, `
			SELECT lb.lesson_id::text, lb.id::text
			FROM lesson_blocks lb
			WHERE lb.task_id = $1
			  AND lb.is_published = TRUE
			ORDER BY lb.position ASC
			LIMIT 1
		`, claimed.TaskID).Scan(&lessonID, &blockID)
		if err == nil {
			if upsertErr := a.upsertLessonBlockCompletion(
				ctx,
				tx,
				claimed.UserID,
				lessonID,
				blockID,
				"submission",
				claimed.SubmissionID,
			); upsertErr != nil {
				return upsertErr
			}
		} else if err != pgx.ErrNoRows {
			return err
		}
	}

	if err := a.applyAchievements(ctx, tx, claimed.UserID); err != nil {
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
	var status string
	err = tx.QueryRow(ctx, `
		SELECT processing_attempts, status
		FROM submissions
		WHERE id = $1
		FOR UPDATE
	`, submissionID).Scan(&processingAttempts, &status)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil
		}
		return err
	}
	if status != "processing" && status != "queued" {
		return nil
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
