package app

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/md5"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
)

var pendingPaymentStatuses = map[string]struct{}{
	"creating":       {},
	"pending":        {},
	"processing":     {},
	"underpaid":      {},
	"pending_config": {},
}

var successPaymentStatuses = map[string]struct{}{
	"paid":      {},
	"succeeded": {},
	"success":   {},
	"overpaid":  {},
}

var revocationPaymentStatuses = map[string]struct{}{
	"refunded":   {},
	"reversed":   {},
	"chargeback": {},
}

type cardlinkBillCreateResponse struct {
	Success     any    `json:"success"`
	LinkURL     string `json:"link_url"`
	LinkPageURL string `json:"link_page_url"`
	BillID      string `json:"bill_id"`
	Message     string `json:"message"`
	Error       string `json:"error"`
}

type cardlinkBillStatusResponse struct {
	ID      string `json:"id"`
	OrderID string `json:"order_id"`
	Status  string `json:"status"`
	Type    string `json:"type"`
	Success any    `json:"success"`
}

func (a *App) ListPlans(c *gin.Context) {
	rows, err := a.DB.Query(c.Request.Context(), `
		SELECT
			code,
			title,
			description,
			price_rub,
			daily_submission_limit,
			has_priority_queue,
			has_personal_hints,
			has_extended_analytics,
			max_courses
		FROM plans
		WHERE is_public = TRUE
		ORDER BY price_rub ASC
	`)
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer rows.Close()

	items := []gin.H{}
	for rows.Next() {
		var code, title, description string
		var price, daily int
		var priority, hints, analytics bool
		var maxCoursesRaw sql.NullInt32
		if err := rows.Scan(&code, &title, &description, &price, &daily, &priority, &hints, &analytics, &maxCoursesRaw); err != nil {
			internalServerError(c, err)
			return
		}
		var maxCourses *int
		if maxCoursesRaw.Valid {
			value := int(maxCoursesRaw.Int32)
			maxCourses = &value
		}
		items = append(items, gin.H{
			"code": code, "title": title, "description": description, "priceRub": price,
			"dailySubmissionLimit": daily,
			"maxCourses":           maxCourses,
			"features":             gin.H{"priorityQueue": priority, "personalHints": hints, "extendedAnalytics": analytics},
		})
	}
	c.JSON(http.StatusOK, gin.H{"items": items})
}

func (a *App) GetSubscription(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	if err := a.ensureSubscriptionState(c.Request.Context(), uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	var code, title, status string
	var price int
	var endsAt *time.Time
	var autoRenew bool
	var maxCoursesRaw sql.NullInt32
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT p.code, p.title, p.price_rub, s.status, s.ends_at, s.auto_renew, p.max_courses
		FROM subscriptions s
		JOIN plans p ON p.id = s.plan_id
		WHERE s.user_id = $1
		  AND s.status = 'active'
		  AND (s.ends_at IS NULL OR s.ends_at > NOW())
		ORDER BY s.starts_at DESC, s.created_at DESC
		LIMIT 1
	`, uctx.ID).Scan(&code, &title, &price, &status, &endsAt, &autoRenew, &maxCoursesRaw)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"code":       technicalFreePlanCode,
			"title":      "Без подписки",
			"status":     "active",
			"priceRub":   0,
			"maxCourses": 0,
			"autoRenew":  true,
		})
		return
	}
	var maxCourses *int
	if maxCoursesRaw.Valid {
		value := int(maxCoursesRaw.Int32)
		maxCourses = &value
	}
	c.JSON(http.StatusOK, gin.H{
		"code":       code,
		"title":      title,
		"status":     status,
		"priceRub":   price,
		"maxCourses": maxCourses,
		"endsAt":     endsAt,
		"autoRenew":  autoRenew,
	})
}

func (a *App) CreateCheckout(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	if err := a.ensureSubscriptionState(c.Request.Context(), uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	var req struct {
		PlanCode string `json:"planCode" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	req.PlanCode = strings.ToLower(strings.TrimSpace(req.PlanCode))
	if req.PlanCode == technicalFreePlanCode {
		c.JSON(http.StatusBadRequest, APIError{Error: "technical free plan does not require checkout"})
		return
	}

	var planID, planTitle string
	var amount int
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT id, title, price_rub
		FROM plans
		WHERE code = $1
		  AND is_public = TRUE
	`, req.PlanCode).Scan(&planID, &planTitle, &amount)
	if err != nil {
		notFound(c, "plan not found")
		return
	}

	var existingPaymentID, existingStatus, existingCheckoutURL string
	err = a.DB.QueryRow(c.Request.Context(), `
		SELECT provider_payment_id, status, COALESCE(checkout_url, '')
		FROM payments
		WHERE user_id = $1
		  AND plan_id = $2
		  AND status IN ('creating', 'pending', 'processing', 'underpaid', 'pending_config')
		  AND created_at >= NOW() - interval '30 minutes'
		ORDER BY created_at DESC
		LIMIT 1
	`, uctx.ID, planID).Scan(&existingPaymentID, &existingStatus, &existingCheckoutURL)
	if err == nil {
		c.JSON(http.StatusOK, gin.H{
			"provider":    "cardlink",
			"paymentId":   existingPaymentID,
			"checkoutUrl": existingCheckoutURL,
			"status":      existingStatus,
			"message":     "Найден уже созданный checkout. Используем существующую платежную сессию.",
		})
		return
	}
	if err != pgx.ErrNoRows {
		internalServerError(c, err)
		return
	}

	ready, missing := a.cardlinkCheckoutReadiness()
	if !ready {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error":   "payment provider is not configured",
			"details": "Cardlink checkout disabled: configure required env values and provider-side API access",
			"missing": missing,
			"status":  "pending_config",
		})
		return
	}

	paymentID := "LCPAY-" + strings.ToUpper(strings.ReplaceAll(uuid.NewString(), "-", ""))[:18]
	checkoutURL := strings.TrimRight(a.Cfg.FrontendURL, "/") + "/billing?pendingPayment=" + url.QueryEscape(paymentID)
	status := "creating"
	rawPayload := gin.H{
		"planCode":  req.PlanCode,
		"planTitle": planTitle,
		"mode":      "creating_checkout",
	}

	if _, err := a.DB.Exec(c.Request.Context(), `
		INSERT INTO payments(provider_payment_id, provider_bill_id, user_id, plan_id, provider, amount_rub, status, checkout_url, raw_payload)
		VALUES($1, NULL, $2, $3, 'cardlink', $4, $5, $6, $7::jsonb)
	`, paymentID, uctx.ID, planID, amount, status, checkoutURL, jsonMarshal(rawPayload)); err != nil {
		internalServerError(c, err)
		return
	}

	linkURL, billID, providerPayload, createErr := a.createCardlinkBill(c, paymentID, amount, planTitle, req.PlanCode)
	if createErr != nil {
		providerStatus := "provider_error"
		responseStatus := http.StatusBadGateway
		responseBody := any(APIError{
			Error:     "internal server error",
			RequestID: requestIDFromContext(c),
		})
		providerMode := "provider_error"
		providerDetails := strings.TrimSpace(createErr.Error())
		providerMissing := []string{}

		isProviderBlocked, blockedDetails, missing := a.classifyCardlinkCreateBillIssue(createErr)
		if isProviderBlocked {
			providerStatus = "pending_config"
			providerMode = "provider_pending_config"
			providerDetails = blockedDetails
			providerMissing = missing
			responseStatus = http.StatusServiceUnavailable
			responseBody = gin.H{
				"error":     "payment provider is not configured",
				"details":   blockedDetails,
				"missing":   missing,
				"status":    "pending_config",
				"paymentId": paymentID,
				"provider":  "cardlink",
			}
		}

		_, _ = a.DB.Exec(c.Request.Context(), `
			UPDATE payments
			SET status = $2,
			    raw_payload = $3::jsonb,
			    updated_at = NOW()
			WHERE provider = 'cardlink' AND provider_payment_id = $1
		`, paymentID, providerStatus, jsonMarshal(gin.H{
			"planCode":      req.PlanCode,
			"planTitle":     planTitle,
			"providerError": createErr.Error(),
			"providerMode":  providerMode,
			"details":       providerDetails,
			"missing":       providerMissing,
		}))
		c.JSON(responseStatus, responseBody)
		return
	}

	status = "pending"
	checkoutURL = linkURL
	rawPayload = gin.H{
		"planCode":        req.PlanCode,
		"planTitle":       planTitle,
		"billId":          billID,
		"providerPayload": providerPayload,
		"mode":            "api_checkout",
	}
	if _, err := a.DB.Exec(c.Request.Context(), `
		UPDATE payments
		SET provider_bill_id = $2,
		    status = $3,
		    checkout_url = $4,
		    raw_payload = $5::jsonb,
		    updated_at = NOW()
		WHERE provider = 'cardlink' AND provider_payment_id = $1
	`, paymentID, billID, status, checkoutURL, jsonMarshal(rawPayload)); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"provider":    "cardlink",
		"paymentId":   paymentID,
		"checkoutUrl": checkoutURL,
		"status":      status,
		"message":     "Платежная сессия сформирована.",
	})
}

func (a *App) ApplyPromoCode(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	if err := a.ensureSubscriptionState(c.Request.Context(), uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	var req struct {
		Code string `json:"code" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	code := strings.ToUpper(strings.TrimSpace(req.Code))
	if code == "" {
		badRequest(c, fmt.Errorf("promo code is required"))
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	if err := a.ensureSubscriptionStateTx(c.Request.Context(), tx, uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	var (
		promoID        string
		planID         string
		planCode       string
		planTitle      string
		planPriceRub   int
		promoPaymentID string
		isActive       bool
		isReusable     bool
		redeemedByID   sql.NullString
		redeemedAtRaw  sql.NullTime
	)
	err = tx.QueryRow(c.Request.Context(), `
		SELECT
			pc.id,
			pc.plan_id,
			p.code,
			p.title,
			p.price_rub,
			pc.is_active,
			pc.is_reusable,
			pc.redeemed_by_user_id::text,
			pc.redeemed_at
		FROM promo_codes pc
		JOIN plans p ON p.id = pc.plan_id
		WHERE UPPER(pc.code) = $1
		FOR UPDATE
	`, code).Scan(
		&promoID,
		&planID,
		&planCode,
		&planTitle,
		&planPriceRub,
		&isActive,
		&isReusable,
		&redeemedByID,
		&redeemedAtRaw,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			if suggestion, ok := a.suggestPromoCodeWithSingleExtraCharTx(c.Request.Context(), tx, code); ok {
				notFound(c, fmt.Sprintf("promo code not found; did you mean %s?", suggestion))
				return
			}
			notFound(c, "promo code not found")
			return
		}
		internalServerError(c, err)
		return
	}

	if planCode == technicalFreePlanCode {
		c.JSON(http.StatusConflict, APIError{Error: "promo code points to technical non-learning plan"})
		return
	}
	if !isActive {
		c.JSON(http.StatusConflict, APIError{Error: "promo code is disabled"})
		return
	}
	if !isReusable {
		if redeemedByID.Valid && strings.TrimSpace(redeemedByID.String) != "" {
			if strings.TrimSpace(redeemedByID.String) == uctx.ID {
				c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed by this account"})
				return
			}
			c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed"})
			return
		}
		if redeemedAtRaw.Valid {
			c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed"})
			return
		}
	}

	promoPaymentID = uuid.NewString()
	promoProviderPaymentID := "PROMO-" + promoID
	if isReusable {
		promoProviderPaymentID = fmt.Sprintf("PROMO-%s-%s", promoID, promoPaymentID)
	}

	if !isReusable {
		var existingPaymentUserID sql.NullString
		var existingPaymentCreatedAt time.Time
		err = tx.QueryRow(c.Request.Context(), `
			SELECT id::text, user_id::text, created_at
			FROM payments
			WHERE provider = 'promo'
			  AND provider_payment_id = $1
			ORDER BY created_at DESC
			LIMIT 1
		`, promoProviderPaymentID).Scan(new(string), &existingPaymentUserID, &existingPaymentCreatedAt)
		if err != nil && err != pgx.ErrNoRows {
			internalServerError(c, err)
			return
		}
		if err == nil {
			if !redeemedByID.Valid && !redeemedAtRaw.Valid {
				if _, err := tx.Exec(c.Request.Context(), `
					UPDATE promo_codes
					SET redeemed_by_user_id = $2,
					    redeemed_at = COALESCE(redeemed_at, $3),
					    updated_at = NOW()
					WHERE id = $1
			`, promoID, existingPaymentUserID, existingPaymentCreatedAt); err != nil {
					internalServerError(c, err)
					return
				}

				redeemedByID.String = existingPaymentUserID.String
				redeemedByID.Valid = existingPaymentUserID.Valid && strings.TrimSpace(existingPaymentUserID.String) != ""
				redeemedAtRaw.Time = existingPaymentCreatedAt
				redeemedAtRaw.Valid = true
			}

			if strings.TrimSpace(existingPaymentUserID.String) == uctx.ID {
				c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed by this account"})
				return
			}
			c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed"})
			return
		}
	}

	insertPromoPaymentErr := tx.QueryRow(c.Request.Context(), `
		INSERT INTO payments(
			id, user_id, plan_id, provider, provider_payment_id, amount_rub, status, checkout_url, raw_payload, provider_bill_id
		)
		VALUES($1, $2, $3, 'promo', $4, $5, 'paid', NULL, $6::jsonb, NULL)
		RETURNING id
	`, promoPaymentID, uctx.ID, planID, promoProviderPaymentID, planPriceRub, jsonMarshal(gin.H{
		"mode":      "promo_code_redeem",
		"promoId":   promoID,
		"promoCode": code,
		"planCode":  planCode,
		"planTitle": planTitle,
	})).Scan(&promoPaymentID)
	if insertPromoPaymentErr != nil {
		if isReusable {
			internalServerError(c, insertPromoPaymentErr)
			return
		}
		var (
			existingPaymentUserID    sql.NullString
			existingPaymentCreatedAt time.Time
			pgErr                    *pgconn.PgError
		)
		var pgCheckErr error = insertPromoPaymentErr
		if !errors.As(pgCheckErr, &pgErr) || pgErr.Code != "23505" {
			internalServerError(c, insertPromoPaymentErr)
			return
		}

		err = tx.QueryRow(c.Request.Context(), `
			SELECT user_id::text, created_at
			FROM payments
			WHERE provider = 'promo'
			  AND provider_payment_id = $1
			ORDER BY created_at DESC
			LIMIT 1
		`, promoProviderPaymentID).Scan(&existingPaymentUserID, &existingPaymentCreatedAt)
		if err != nil {
			internalServerError(c, err)
			return
		}

		if !redeemedByID.Valid && !redeemedAtRaw.Valid {
			if _, err := tx.Exec(c.Request.Context(), `
				UPDATE promo_codes
				SET redeemed_by_user_id = $2,
				    redeemed_at = COALESCE(redeemed_at, $3),
				    updated_at = NOW()
				WHERE id = $1
			`, promoID, existingPaymentUserID, existingPaymentCreatedAt); err != nil {
				internalServerError(c, err)
				return
			}

			redeemedByID.String = existingPaymentUserID.String
			redeemedByID.Valid = existingPaymentUserID.Valid && strings.TrimSpace(existingPaymentUserID.String) != ""
			redeemedAtRaw.Time = existingPaymentCreatedAt
			redeemedAtRaw.Valid = true
		}

		if strings.TrimSpace(existingPaymentUserID.String) == uctx.ID {
			c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed by this account"})
			return
		}
		c.JSON(http.StatusConflict, APIError{Error: "promo code already redeemed"})
		return
	}

	if err := a.activateSubscriptionFromPaymentTx(c.Request.Context(), tx, uctx.ID, planID, promoPaymentID); err != nil {
		internalServerError(c, err)
		return
	}

	if !isReusable {
		if _, err := tx.Exec(c.Request.Context(), `
			UPDATE promo_codes
			SET redeemed_by_user_id = $2,
			    redeemed_at = NOW(),
			    updated_at = NOW()
			WHERE id = $1
		`, promoID, uctx.ID); err != nil {
			internalServerError(c, err)
			return
		}
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":    "promo_applied",
		"code":      code,
		"planCode":  planCode,
		"planTitle": planTitle,
	})
}

func (a *App) suggestPromoCodeWithSingleExtraCharTx(ctx context.Context, tx pgx.Tx, code string) (string, bool) {
	// Typical user typo: one extra character in an otherwise valid code.
	// Example: PREM26AB0B1C2 -> PREM26A0B1C2
	if len(code) != 13 {
		return "", false
	}

	seen := make(map[string]struct{}, len(code))
	candidates := make([]string, 0, len(code))
	for i := 0; i < len(code); i++ {
		candidate := code[:i] + code[i+1:]
		if len(candidate) != 12 {
			continue
		}
		if _, exists := seen[candidate]; exists {
			continue
		}
		seen[candidate] = struct{}{}
		candidates = append(candidates, candidate)
	}
	if len(candidates) == 0 {
		return "", false
	}

	rows, err := tx.Query(ctx, `
		SELECT code
		FROM promo_codes
		WHERE UPPER(code) = ANY($1::text[])
		  AND is_active = TRUE
		  AND (is_reusable OR (redeemed_at IS NULL AND redeemed_by_user_id IS NULL))
	`, candidates)
	if err != nil {
		return "", false
	}
	defer rows.Close()

	matches := make([]string, 0, 2)
	for rows.Next() {
		var match string
		if scanErr := rows.Scan(&match); scanErr != nil {
			return "", false
		}
		matches = append(matches, strings.ToUpper(strings.TrimSpace(match)))
		if len(matches) > 1 {
			return "", false
		}
	}
	if rows.Err() != nil {
		return "", false
	}
	if len(matches) == 1 && matches[0] != "" {
		return matches[0], true
	}
	return "", false
}

func (a *App) CancelSubscription(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	if err := a.ensureSubscriptionStateTx(c.Request.Context(), tx, uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}
	current, exists, err := a.loadActiveSubscriptionTx(c.Request.Context(), tx, uctx.ID, true)
	if err != nil {
		internalServerError(c, err)
		return
	}
	if !exists || current.PlanCode == technicalFreePlanCode {
		if err := tx.Commit(c.Request.Context()); err != nil {
			internalServerError(c, err)
			return
		}
		c.JSON(http.StatusOK, gin.H{
			"status":   "already_free",
			"planCode": technicalFreePlanCode,
		})
		return
	}

	var endsAt time.Time
	if err := tx.QueryRow(c.Request.Context(), `
		UPDATE subscriptions
		SET auto_renew = FALSE,
		    ends_at = COALESCE(ends_at, NOW() + interval '30 day'),
		    updated_at = NOW()
		WHERE id = $1
		RETURNING ends_at
	`, current.ID).Scan(&endsAt); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":              "cancel_at_period_end",
		"planCode":            current.PlanCode,
		"autoRenew":           false,
		"accessUntil":         endsAt,
		"cancelEffectiveAt":   endsAt,
		"subscriptionUpdated": true,
	})
}

func (a *App) GetPaymentStatus(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}
	if err := a.ensureSubscriptionState(c.Request.Context(), uctx.ID); err != nil {
		internalServerError(c, err)
		return
	}

	paymentID := strings.TrimSpace(c.Param("paymentID"))
	if paymentID == "" {
		badRequest(c, fmt.Errorf("payment id is required"))
		return
	}

	syncRequested := strings.EqualFold(c.Query("sync"), "1") || strings.EqualFold(c.Query("sync"), "true")
	if syncRequested {
		_ = a.trySyncPendingCardlinkPayment(c.Request.Context(), uctx.ID, paymentID)
	}

	var (
		orderID     string
		billID      string
		status      string
		checkoutURL string
		amountRub   int
		planCode    string
		planTitle   string
		createdAt   time.Time
		updatedAt   time.Time
	)

	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT p.provider_payment_id,
		       COALESCE(p.provider_bill_id, ''),
		       p.status,
		       COALESCE(p.checkout_url, ''),
		       p.amount_rub,
		       pl.code,
		       pl.title,
		       p.created_at,
		       p.updated_at
		FROM payments p
		JOIN plans pl ON pl.id = p.plan_id
		WHERE p.user_id = $1
		  AND p.provider = 'cardlink'
		  AND p.provider_payment_id = $2
		ORDER BY p.created_at DESC
		LIMIT 1
	`, uctx.ID, paymentID).Scan(
		&orderID,
		&billID,
		&status,
		&checkoutURL,
		&amountRub,
		&planCode,
		&planTitle,
		&createdAt,
		&updatedAt,
	)
	if err != nil {
		notFound(c, "payment not found")
		return
	}

	var subCode, subStatus string
	var subEndsAt *time.Time
	var subAutoRenew bool
	var subMaxCoursesRaw sql.NullInt32
	err = a.DB.QueryRow(c.Request.Context(), `
		SELECT p.code, s.status, s.ends_at, s.auto_renew, p.max_courses
		FROM subscriptions s
		JOIN plans p ON p.id = s.plan_id
		WHERE s.user_id = $1
		  AND s.status = 'active'
		  AND (s.ends_at IS NULL OR s.ends_at > NOW())
		ORDER BY s.starts_at DESC, s.created_at DESC
		LIMIT 1
	`, uctx.ID).Scan(&subCode, &subStatus, &subEndsAt, &subAutoRenew, &subMaxCoursesRaw)
	if err != nil {
		subCode = technicalFreePlanCode
		subStatus = "active"
		subAutoRenew = true
	}
	var subMaxCourses *int
	if subMaxCoursesRaw.Valid {
		value := int(subMaxCoursesRaw.Int32)
		subMaxCourses = &value
	}

	normalizedStatus := normalizePaymentStatus(status)
	c.JSON(http.StatusOK, gin.H{
		"payment": gin.H{
			"paymentId":    orderID,
			"provider":     "cardlink",
			"providerBill": billID,
			"status":       normalizedStatus,
			"terminal":     !isPendingPaymentStatus(normalizedStatus),
			"canRetry":     normalizedStatus == "failed" || normalizedStatus == "provider_error" || normalizedStatus == "underpaid" || normalizedStatus == "pending_config",
			"checkoutUrl":  checkoutURL,
			"amountRub":    amountRub,
			"planCode":     planCode,
			"planTitle":    planTitle,
			"createdAt":    createdAt,
			"updatedAt":    updatedAt,
		},
		"subscription": gin.H{
			"code":       subCode,
			"status":     subStatus,
			"maxCourses": subMaxCourses,
			"endsAt":     subEndsAt,
			"autoRenew":  subAutoRenew,
		},
	})
}

func (a *App) CardlinkWebhook(c *gin.Context) {
	raw, err := io.ReadAll(io.LimitReader(c.Request.Body, 1024*1024))
	if err != nil {
		internalServerError(c, err)
		return
	}

	paymentOrderID, providerBillID, normalizedStatus, payloadJSON, err := a.parseCardlinkWebhook(c, raw)
	if err != nil {
		c.JSON(http.StatusUnauthorized, APIError{Error: "invalid webhook payload"})
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var paymentID, userID, planID, currentPaymentStatus string
	err = tx.QueryRow(c.Request.Context(), `
		SELECT id, user_id, plan_id, status
		FROM payments
		WHERE provider = 'cardlink' AND provider_payment_id = $1
		FOR UPDATE
	`, paymentOrderID).Scan(&paymentID, &userID, &planID, &currentPaymentStatus)
	if err != nil {
		notFound(c, "payment not found")
		return
	}

	if err := a.applyPaymentStatusTransitionTx(
		c.Request.Context(),
		tx,
		paymentID,
		userID,
		planID,
		currentPaymentStatus,
		normalizedStatus,
		providerBillID,
		payloadJSON,
	); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status":       "ok",
		"paymentId":    paymentOrderID,
		"paymentState": normalizedStatus,
	})
}

func (a *App) CardlinkReturnSuccess(c *gin.Context) {
	a.handleCardlinkReturn(c, "paid")
}

func (a *App) CardlinkReturnFail(c *gin.Context) {
	a.handleCardlinkReturn(c, "failed")
}

func (a *App) handleCardlinkReturn(c *gin.Context, fallbackStatus string) {
	raw, err := io.ReadAll(io.LimitReader(c.Request.Body, 1024*1024))
	if err != nil {
		internalServerError(c, err)
		return
	}
	values, parseErr := url.ParseQuery(string(raw))
	if parseErr != nil || len(values) == 0 {
		_ = c.Request.ParseForm()
		if len(c.Request.Form) > 0 {
			values = c.Request.Form
		}
	}

	paymentOrderID := strings.TrimSpace(values.Get("InvId"))
	outSum := strings.TrimSpace(values.Get("OutSum"))
	signature := strings.TrimSpace(values.Get("SignatureValue"))
	statusRaw := strings.TrimSpace(values.Get("Status"))
	providerBillID := strings.TrimSpace(values.Get("TrsId"))
	if paymentOrderID == "" {
		badRequest(c, fmt.Errorf("missing InvId in cardlink return"))
		return
	}
	if verifyErr := a.verifyCardlinkFormSignature(outSum, paymentOrderID, signature); verifyErr != nil {
		c.JSON(http.StatusUnauthorized, APIError{Error: "invalid return payload"})
		return
	}

	normalizedStatus := normalizePaymentStatus(statusRaw)
	if normalizedStatus == "" {
		normalizedStatus = normalizePaymentStatus(fallbackStatus)
	}
	payloadJSON := jsonMarshal(gin.H{
		"mode":          "cardlink_return_redirect",
		"invId":         paymentOrderID,
		"trsId":         providerBillID,
		"statusRaw":     statusRaw,
		"fallbackState": fallbackStatus,
		"outSum":        outSum,
		"raw":           string(raw),
		"query":         c.Request.URL.RawQuery,
	})

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var paymentID, userID, planID, currentPaymentStatus string
	err = tx.QueryRow(c.Request.Context(), `
		SELECT id, user_id, plan_id, status
		FROM payments
		WHERE provider = 'cardlink' AND provider_payment_id = $1
		FOR UPDATE
	`, paymentOrderID).Scan(&paymentID, &userID, &planID, &currentPaymentStatus)
	if err != nil {
		if err == pgx.ErrNoRows {
			a.redirectToBilling(c, paymentOrderID, "not_found")
			return
		}
		internalServerError(c, err)
		return
	}

	if err := a.applyPaymentStatusTransitionTx(
		c.Request.Context(),
		tx,
		paymentID,
		userID,
		planID,
		currentPaymentStatus,
		normalizedStatus,
		providerBillID,
		payloadJSON,
	); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	a.redirectToBilling(c, paymentOrderID, normalizedStatus)
}

func normalizePaymentStatus(raw string) string {
	switch strings.ToLower(strings.TrimSpace(raw)) {
	case "new", "created", "pending":
		return "pending"
	case "process", "processing", "in_progress", "authorized":
		return "processing"
	case "underpaid":
		return "underpaid"
	case "success", "succeeded", "paid", "overpaid", "completed":
		return "paid"
	case "fail", "failed", "declined", "cancelled", "canceled", "expired":
		return "failed"
	case "refund", "refunded":
		return "refunded"
	case "reversed":
		return "reversed"
	case "chargeback":
		return "chargeback"
	case "provider_error":
		return "provider_error"
	default:
		return strings.ToLower(strings.TrimSpace(raw))
	}
}

func isPendingPaymentStatus(status string) bool {
	_, ok := pendingPaymentStatuses[normalizePaymentStatus(status)]
	return ok
}

func isSuccessPaymentStatus(status string) bool {
	_, ok := successPaymentStatuses[normalizePaymentStatus(status)]
	return ok
}

func isRevocationPaymentStatus(status string) bool {
	_, ok := revocationPaymentStatuses[normalizePaymentStatus(status)]
	return ok
}

func (a *App) parseCardlinkWebhook(c *gin.Context, raw []byte) (paymentOrderID, providerBillID, status, payloadJSON string, err error) {
	contentType := strings.ToLower(strings.TrimSpace(c.ContentType()))
	isForm := strings.Contains(contentType, "application/x-www-form-urlencoded")
	if !isForm {
		rawLower := strings.ToLower(string(raw))
		isForm = strings.Contains(rawLower, "invid=") && strings.Contains(rawLower, "signaturevalue=")
	}

	if isForm {
		values, parseErr := url.ParseQuery(string(raw))
		if parseErr != nil {
			return "", "", "", "", fmt.Errorf("parse form payload: %w", parseErr)
		}

		invID := strings.TrimSpace(values.Get("InvId"))
		statusRaw := strings.TrimSpace(values.Get("Status"))
		signature := strings.TrimSpace(values.Get("SignatureValue"))
		outSum := strings.TrimSpace(values.Get("OutSum"))
		trsID := strings.TrimSpace(values.Get("TrsId"))
		if invID == "" || statusRaw == "" {
			return "", "", "", "", fmt.Errorf("missing InvId or Status in postback payload")
		}
		if verifyErr := a.verifyCardlinkFormSignature(outSum, invID, signature); verifyErr != nil {
			return "", "", "", "", verifyErr
		}

		payload := gin.H{
			"mode":       "cardlink_form_postback",
			"invId":      invID,
			"trsId":      trsID,
			"statusRaw":  statusRaw,
			"outSum":     outSum,
			"currencyIn": strings.TrimSpace(values.Get("CurrencyIn")),
			"custom":     strings.TrimSpace(values.Get("custom")),
			"raw":        string(raw),
		}
		return invID, trsID, normalizePaymentStatus(statusRaw), jsonMarshal(payload), nil
	}

	token := c.GetHeader("X-Cardlink-Token")
	if token != a.Cfg.CardlinkWebhookToken {
		return "", "", "", "", fmt.Errorf("invalid webhook token")
	}
	if verifyErr := a.verifyCardlinkWebhookSignature(raw, c.GetHeader("X-Cardlink-Signature")); verifyErr != nil {
		return "", "", "", "", verifyErr
	}

	var payload struct {
		PaymentID string `json:"paymentId"`
		Status    string `json:"status"`
		BillID    string `json:"billId"`
	}
	if parseErr := json.Unmarshal(raw, &payload); parseErr != nil {
		return "", "", "", "", fmt.Errorf("decode json payload: %w", parseErr)
	}
	if strings.TrimSpace(payload.PaymentID) == "" || strings.TrimSpace(payload.Status) == "" {
		return "", "", "", "", fmt.Errorf("missing paymentId or status in json payload")
	}

	jsonPayload := jsonMarshal(gin.H{
		"mode":      "legacy_json_webhook",
		"paymentId": payload.PaymentID,
		"billId":    payload.BillID,
		"statusRaw": payload.Status,
		"raw":       string(raw),
	})
	return strings.TrimSpace(payload.PaymentID), strings.TrimSpace(payload.BillID), normalizePaymentStatus(payload.Status), jsonPayload, nil
}

func (a *App) applyPaymentStatusTransitionTx(ctx context.Context, tx pgx.Tx, paymentID, userID, planID, currentStatus, newStatus, providerBillID, payloadJSON string) error {
	normalizedNew := normalizePaymentStatus(newStatus)
	normalizedOld := normalizePaymentStatus(currentStatus)

	if payloadJSON == "" {
		payloadJSON = "{}"
	}
	if _, err := tx.Exec(ctx, `
		UPDATE payments
		SET status = $2,
		    provider_bill_id = COALESCE(NULLIF($3, ''), provider_bill_id),
		    raw_payload = $4::jsonb,
		    updated_at = NOW()
		WHERE id = $1
	`, paymentID, normalizedNew, providerBillID, payloadJSON); err != nil {
		return err
	}
	if _, err := tx.Exec(ctx, `
		INSERT INTO payment_events(payment_id, event_type, raw_payload)
		VALUES($1, $2, $3::jsonb)
	`, paymentID, normalizedNew, payloadJSON); err != nil {
		return err
	}

	if !isSuccessPaymentStatus(normalizedOld) && isSuccessPaymentStatus(normalizedNew) {
		if err := a.activateSubscriptionFromPaymentTx(ctx, tx, userID, planID, paymentID); err != nil {
			return err
		}
	}
	if isSuccessPaymentStatus(normalizedOld) && isRevocationPaymentStatus(normalizedNew) {
		if err := a.revokeSubscriptionFromPaymentTx(ctx, tx, userID, paymentID); err != nil {
			return err
		}
	}
	return nil
}

func (a *App) activateSubscriptionFromPaymentTx(ctx context.Context, tx pgx.Tx, userID, planID, paymentID string) error {
	if err := a.ensureSubscriptionStateTx(ctx, tx, userID); err != nil {
		return err
	}

	current, exists, err := a.loadActiveSubscriptionTx(ctx, tx, userID, true)
	if err != nil {
		return err
	}

	if !exists {
		_, err = tx.Exec(ctx, `
			INSERT INTO subscriptions(user_id, plan_id, status, starts_at, ends_at, auto_renew, source_payment_id)
			VALUES($1, $2, 'active', NOW(), NOW() + interval '30 day', TRUE, $3)
		`, userID, planID, paymentID)
		return err
	}

	if current.PlanCode == technicalFreePlanCode {
		if _, err := tx.Exec(ctx, `
			UPDATE subscriptions
			SET status = 'cancelled',
			    auto_renew = FALSE,
			    ends_at = NOW(),
			    updated_at = NOW()
			WHERE id = $1
		`, current.ID); err != nil {
			return err
		}
		_, err = tx.Exec(ctx, `
			INSERT INTO subscriptions(user_id, plan_id, status, starts_at, ends_at, auto_renew, source_payment_id)
			VALUES($1, $2, 'active', NOW(), NOW() + interval '30 day', TRUE, $3)
		`, userID, planID, paymentID)
		return err
	}

	if current.PlanID == planID {
		_, err = tx.Exec(ctx, `
			UPDATE subscriptions
			SET ends_at = GREATEST(COALESCE(ends_at, NOW()), NOW()) + interval '30 day',
			    auto_renew = TRUE,
			    source_payment_id = $2,
			    updated_at = NOW()
			WHERE id = $1
		`, current.ID, paymentID)
		return err
	}

	if _, err := tx.Exec(ctx, `
		UPDATE subscriptions
		SET status = 'cancelled',
		    auto_renew = FALSE,
		    ends_at = NOW(),
		    updated_at = NOW()
		WHERE id = $1
	`, current.ID); err != nil {
		return err
	}

	_, err = tx.Exec(ctx, `
		INSERT INTO subscriptions(user_id, plan_id, status, starts_at, ends_at, auto_renew, source_payment_id)
		VALUES($1, $2, 'active', NOW(), NOW() + interval '30 day', TRUE, $3)
	`, userID, planID, paymentID)
	return err
}

func (a *App) revokeSubscriptionFromPaymentTx(ctx context.Context, tx pgx.Tx, userID, paymentID string) error {
	if _, err := tx.Exec(ctx, `
		UPDATE subscriptions
		SET status = 'cancelled',
		    auto_renew = FALSE,
		    ends_at = NOW(),
		    updated_at = NOW()
		WHERE user_id = $1
		  AND status = 'active'
		  AND source_payment_id = $2
	`, userID, paymentID); err != nil {
		return err
	}
	return a.ensureFreeSubscriptionTx(ctx, tx, userID)
}

func (a *App) trySyncPendingCardlinkPayment(ctx context.Context, userID, orderPaymentID string) error {
	if !a.cardlinkReadyForCheckout() {
		return nil
	}

	var paymentID, planID, status, billID string
	err := a.DB.QueryRow(ctx, `
		SELECT id, plan_id, status, COALESCE(provider_bill_id, '')
		FROM payments
		WHERE user_id = $1
		  AND provider = 'cardlink'
		  AND provider_payment_id = $2
		ORDER BY created_at DESC
		LIMIT 1
	`, userID, orderPaymentID).Scan(&paymentID, &planID, &status, &billID)
	if err != nil {
		return err
	}
	if !isPendingPaymentStatus(status) || strings.TrimSpace(billID) == "" {
		return nil
	}

	syncedStatus, payloadJSON, err := a.fetchCardlinkBillStatus(ctx, billID)
	if err != nil {
		return err
	}
	if normalizePaymentStatus(syncedStatus) == normalizePaymentStatus(status) {
		return nil
	}

	tx, err := a.DB.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	var currentStatus string
	err = tx.QueryRow(ctx, `
		SELECT status
		FROM payments
		WHERE id = $1
		FOR UPDATE
	`, paymentID).Scan(&currentStatus)
	if err != nil {
		return err
	}

	if err := a.applyPaymentStatusTransitionTx(ctx, tx, paymentID, userID, planID, currentStatus, syncedStatus, billID, payloadJSON); err != nil {
		return err
	}
	return tx.Commit(ctx)
}

func (a *App) cardlinkReadyForCheckout() bool {
	ready, _ := a.cardlinkCheckoutReadiness()
	return ready
}

func (a *App) cardlinkCheckoutReadiness() (bool, []string) {
	missing := make([]string, 0, 3)
	base := strings.TrimSpace(a.Cfg.CardlinkBaseURL)
	shopID := strings.TrimSpace(a.Cfg.CardlinkShopID)
	token := strings.TrimSpace(a.Cfg.CardlinkAPIToken)

	if base == "" || strings.Contains(base, "cardlink.example") {
		missing = append(missing, "CARDLINK_BASE_URL")
	}
	if shopID == "" {
		missing = append(missing, "CARDLINK_SHOP_ID (or CARDLINK_MERCHANT_ID)")
	}
	if token == "" {
		missing = append(missing, "CARDLINK_API_TOKEN (or CARDLINK_SECRET)")
	}
	return len(missing) == 0, missing
}

func (a *App) cardlinkAPIEndpoint(path string) string {
	base := strings.TrimRight(strings.TrimSpace(a.Cfg.CardlinkBaseURL), "/")
	if strings.HasSuffix(base, "/api/v1") {
		return base + strings.TrimPrefix(path, "/api/v1")
	}
	return base + path
}

func (a *App) createCardlinkBill(c *gin.Context, orderID string, amountRub int, planTitle, planCode string) (linkURL, billID string, payloadJSON string, err error) {
	form := url.Values{}
	form.Set("amount", strconv.Itoa(amountRub))
	form.Set("shop_id", strings.TrimSpace(a.Cfg.CardlinkShopID))
	form.Set("order_id", orderID)
	form.Set("description", fmt.Sprintf("%s (%s)", planTitle, strings.ToUpper(planCode)))
	form.Set("type", "normal")
	form.Set("currency_in", strings.ToUpper(strings.TrimSpace(a.Cfg.CardlinkCurrencyIn)))
	form.Set("custom", fmt.Sprintf("plan=%s", planCode))
	form.Set("payer_pays_commission", "1")
	form.Set("ttl", strconv.Itoa(a.Cfg.CardlinkBillTTLSeconds))
	if v := strings.TrimSpace(a.Cfg.CardlinkLocale); v != "" {
		form.Set("locale", strings.ToLower(v))
	}
	if v := strings.TrimSpace(a.Cfg.CardlinkSuccessURL); v != "" {
		form.Set("success_url", v)
	}
	if v := strings.TrimSpace(a.Cfg.CardlinkFailURL); v != "" {
		form.Set("fail_url", v)
	}
	if v := strings.TrimSpace(a.Cfg.CardlinkReturnURL); v != "" {
		form.Set("return_url", v)
	}

	endpoint := a.cardlinkAPIEndpoint("/api/v1/bill/create")
	req, err := http.NewRequestWithContext(c.Request.Context(), http.MethodPost, endpoint, strings.NewReader(form.Encode()))
	if err != nil {
		return "", "", "", err
	}
	req.Header.Set("Authorization", "Bearer "+strings.TrimSpace(a.Cfg.CardlinkAPIToken))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "application/json")

	client := &http.Client{Timeout: 20 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", "", "", err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))
	if err != nil {
		return "", "", "", err
	}

	var parsed cardlinkBillCreateResponse
	if err := json.Unmarshal(raw, &parsed); err != nil {
		return "", "", "", fmt.Errorf("decode cardlink response: %w", err)
	}
	if resp.StatusCode >= 300 {
		return "", "", "", fmt.Errorf("cardlink create bill status %d: %s", resp.StatusCode, strings.TrimSpace(string(raw)))
	}

	linkURL = strings.TrimSpace(parsed.LinkPageURL)
	if linkURL == "" {
		linkURL = strings.TrimSpace(parsed.LinkURL)
	}
	billID = strings.TrimSpace(parsed.BillID)
	if linkURL == "" || billID == "" {
		return "", "", "", fmt.Errorf("cardlink create bill response missing link_page_url or bill_id")
	}
	return linkURL, billID, string(raw), nil
}

func (a *App) classifyCardlinkCreateBillIssue(createErr error) (blocked bool, details string, missing []string) {
	raw := strings.TrimSpace(createErr.Error())
	providerMessage, blockedIP := parseCardlinkProviderError(raw)
	normalizedRaw := strings.ToLower(raw)
	normalizedMessage := strings.ToLower(strings.TrimSpace(providerMessage))

	if strings.Contains(normalizedRaw, "api:error.ip_access_denied") || strings.Contains(normalizedMessage, "api:error.ip_access_denied") {
		ipText := strings.TrimSpace(blockedIP)
		if ipText == "" {
			ipText = "<backend-ip>"
		}
		shopID := strings.TrimSpace(a.Cfg.CardlinkShopID)
		if shopID == "" {
			shopID = "<shop-id>"
		}
		details = fmt.Sprintf(
			"Cardlink API отклонил запрос с backend IP %s (api:error.ip_access_denied). Добавьте этот IP в allowlist API для shop %s и повторите checkout.",
			ipText,
			shopID,
		)
		return true, details, []string{
			fmt.Sprintf("Cardlink allowlist: add backend IP %s for shop %s", ipText, shopID),
		}
	}

	return false, "", nil
}

func parseCardlinkProviderError(raw string) (message string, blockedIP string) {
	start := strings.Index(strings.TrimSpace(raw), "{")
	if start < 0 {
		return "", ""
	}
	trimmed := strings.TrimSpace(raw)
	body := strings.TrimSpace(trimmed[start:])
	if body == "" {
		return "", ""
	}

	var payload struct {
		Message string `json:"message"`
		Error   string `json:"error"`
		Errors  struct {
			IP string `json:"ip"`
		} `json:"errors"`
	}
	if err := json.Unmarshal([]byte(body), &payload); err != nil {
		return "", ""
	}
	if strings.TrimSpace(payload.Message) != "" {
		message = strings.TrimSpace(payload.Message)
	} else {
		message = strings.TrimSpace(payload.Error)
	}
	return message, strings.TrimSpace(payload.Errors.IP)
}

func (a *App) fetchCardlinkBillStatus(ctx context.Context, billID string) (status, payloadJSON string, err error) {
	endpoint := a.cardlinkAPIEndpoint("/api/v1/bill/status") + "?id=" + url.QueryEscape(strings.TrimSpace(billID))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, bytes.NewReader(nil))
	if err != nil {
		return "", "", err
	}
	req.Header.Set("Authorization", "Bearer "+strings.TrimSpace(a.Cfg.CardlinkAPIToken))
	req.Header.Set("Accept", "application/json")

	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))
	if err != nil {
		return "", "", err
	}
	if resp.StatusCode >= 300 {
		return "", "", fmt.Errorf("cardlink bill status returned http %d", resp.StatusCode)
	}

	var parsed cardlinkBillStatusResponse
	if err := json.Unmarshal(raw, &parsed); err != nil {
		return "", "", fmt.Errorf("decode cardlink bill status: %w", err)
	}
	if strings.TrimSpace(parsed.Status) == "" {
		return "", "", fmt.Errorf("cardlink bill status payload missing status")
	}

	payload := jsonMarshal(gin.H{
		"mode":      "cardlink_bill_status_sync",
		"billId":    billID,
		"statusRaw": parsed.Status,
		"payload":   string(raw),
	})
	return normalizePaymentStatus(parsed.Status), payload, nil
}

func (a *App) cardlinkReturnCallbackURL(c *gin.Context, result string) string {
	forwardedProto := strings.TrimSpace(c.GetHeader("X-Forwarded-Proto"))
	scheme := ""
	if forwardedProto != "" {
		scheme = strings.TrimSpace(strings.Split(forwardedProto, ",")[0])
	}
	if scheme == "" {
		if c.Request.TLS != nil {
			scheme = "https"
		} else {
			scheme = "http"
		}
	}

	host := strings.TrimSpace(c.GetHeader("X-Forwarded-Host"))
	if host == "" {
		host = strings.TrimSpace(c.Request.Host)
	}
	if host == "" {
		return strings.TrimRight(a.Cfg.FrontendURL, "/") + "/billing"
	}

	return scheme + "://" + host + "/api/v1/payments/cardlink/return/" + url.PathEscape(strings.ToLower(strings.TrimSpace(result)))
}

func (a *App) redirectToBilling(c *gin.Context, paymentID, result string) {
	target := strings.TrimRight(a.Cfg.FrontendURL, "/") + "/billing"
	if strings.TrimSpace(paymentID) != "" {
		target += "?pendingPayment=" + url.QueryEscape(strings.TrimSpace(paymentID))
		if strings.TrimSpace(result) != "" {
			target += "&cardlinkResult=" + url.QueryEscape(strings.TrimSpace(result))
		}
	}
	c.Redirect(http.StatusSeeOther, target)
}

func (a *App) verifyCardlinkWebhookSignature(raw []byte, header string) error {
	secret := strings.TrimSpace(a.Cfg.CardlinkSecret)
	if !a.Cfg.CardlinkRequireSignature {
		return nil
	}
	if secret == "" {
		return fmt.Errorf("CARDLINK_SECRET is empty while signature validation is required")
	}
	header = strings.TrimSpace(header)
	if header == "" {
		return fmt.Errorf("signature header is missing")
	}

	provided := strings.ToLower(header)
	if strings.HasPrefix(provided, "sha256=") {
		provided = strings.TrimPrefix(provided, "sha256=")
	}
	_, err := hex.DecodeString(provided)
	if err != nil {
		return fmt.Errorf("signature is not a valid hex digest")
	}

	mac := hmac.New(sha256.New, []byte(secret))
	_, _ = mac.Write(raw)
	expected := hex.EncodeToString(mac.Sum(nil))
	if !hmac.Equal([]byte(provided), []byte(expected)) {
		return fmt.Errorf("signature mismatch")
	}
	return nil
}

func (a *App) verifyCardlinkFormSignature(outSum, invID, signature string) error {
	token := strings.TrimSpace(a.Cfg.CardlinkAPIToken)
	if token == "" {
		token = strings.TrimSpace(a.Cfg.CardlinkSecret)
	}
	if token == "" {
		return fmt.Errorf("CARDLINK_API_TOKEN is required to verify postback signature")
	}
	if strings.TrimSpace(signature) == "" {
		return fmt.Errorf("signature is missing")
	}

	plain := strings.TrimSpace(outSum) + ":" + strings.TrimSpace(invID) + ":" + token
	sum := md5.Sum([]byte(plain))
	expected := strings.ToUpper(hex.EncodeToString(sum[:]))
	provided := strings.ToUpper(strings.TrimSpace(signature))
	if !hmac.Equal([]byte(provided), []byte(expected)) {
		return fmt.Errorf("signature mismatch")
	}
	return nil
}
