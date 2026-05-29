package app

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
)

type activeSubscription struct {
	ID        string
	PlanID    string
	PlanCode  string
	EndsAt    *time.Time
	AutoRenew bool
}

func (a *App) ensureSubscriptionState(ctx context.Context, userID string) error {
	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	if err := a.ensureSubscriptionStateTx(ctx, tx, userID); err != nil {
		return err
	}
	return tx.Commit(ctx)
}

func (a *App) ensureSubscriptionStateTx(ctx context.Context, tx pgx.Tx, userID string) error {
	if _, err := tx.Exec(ctx, `
		UPDATE subscriptions
		SET status='expired', auto_renew=FALSE, updated_at=NOW()
		WHERE user_id=$1
		  AND status='active'
		  AND ends_at IS NOT NULL
		  AND ends_at <= NOW()
	`, userID); err != nil {
		return fmt.Errorf("expire stale subscriptions: %w", err)
	}

	var exists bool
	if err := tx.QueryRow(ctx, `
		SELECT EXISTS(
			SELECT 1
			FROM subscriptions s
			WHERE s.user_id=$1
			  AND s.status='active'
			  AND (s.ends_at IS NULL OR s.ends_at > NOW())
		)
	`, userID).Scan(&exists); err != nil {
		return fmt.Errorf("check active subscription: %w", err)
	}
	if exists {
		return nil
	}
	return a.ensureFreeSubscriptionTx(ctx, tx, userID)
}

func (a *App) ensureFreeSubscriptionTx(ctx context.Context, tx pgx.Tx, userID string) error {
	var freePlanID string
	if err := tx.QueryRow(ctx, `SELECT id FROM plans WHERE code = $1 LIMIT 1`, technicalFreePlanCode).Scan(&freePlanID); err != nil {
		return fmt.Errorf("resolve free plan: %w", err)
	}

	if _, err := tx.Exec(ctx, `
		INSERT INTO subscriptions(user_id, plan_id, status, starts_at, ends_at, auto_renew, source_payment_id)
		VALUES($1, $2, 'active', NOW(), NULL, TRUE, NULL)
		ON CONFLICT DO NOTHING
	`, userID, freePlanID); err != nil {
		return fmt.Errorf("insert fallback free subscription: %w", err)
	}
	return nil
}

func (a *App) loadActiveSubscriptionTx(ctx context.Context, tx pgx.Tx, userID string, forUpdate bool) (activeSubscription, bool, error) {
	query := `
		SELECT s.id, s.plan_id, p.code, s.ends_at, s.auto_renew
		FROM subscriptions s
		JOIN plans p ON p.id = s.plan_id
		WHERE s.user_id = $1
		  AND s.status = 'active'
		  AND (s.ends_at IS NULL OR s.ends_at > NOW())
		ORDER BY s.starts_at DESC, s.created_at DESC
		LIMIT 1
	`
	if forUpdate {
		query += " FOR UPDATE"
	}

	var out activeSubscription
	if err := tx.QueryRow(ctx, query, userID).Scan(&out.ID, &out.PlanID, &out.PlanCode, &out.EndsAt, &out.AutoRenew); err != nil {
		if err == pgx.ErrNoRows {
			return activeSubscription{}, false, nil
		}
		return activeSubscription{}, false, err
	}
	return out, true, nil
}
