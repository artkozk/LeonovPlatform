package app

import (
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"
	"unicode"
	"unicode/utf8"

	"leonovcare/backend/internal/security"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgconn"
)

type registerRequest struct {
	Email     string `json:"email" binding:"required,email"`
	FirstName string `json:"firstName" binding:"required,min=1,max=64"`
	LastName  string `json:"lastName" binding:"required,min=1,max=64"`
	Nickname  string `json:"nickname" binding:"required,min=3,max=32"`
	Password  string `json:"password" binding:"required,min=8,max=128"`
}

type loginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

type refreshRequest struct {
	RefreshToken string `json:"refreshToken" binding:"required"`
}

type tokenResponse struct {
	AccessToken     string `json:"accessToken"`
	RefreshToken    string `json:"refreshToken"`
	AccessTokenTTL  string `json:"accessTokenTtl"`
	RefreshTokenTTL string `json:"refreshTokenTtl"`
	EmailVerified   bool   `json:"emailVerified"`
	CurrentPlan     string `json:"currentPlan"`
}

func (a *App) Register(c *gin.Context) {
	var req registerRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	req.Email = normalizeEmail(req.Email)
	req.FirstName = strings.TrimSpace(req.FirstName)
	req.LastName = strings.TrimSpace(req.LastName)
	req.Nickname = normalizeNickname(req.Nickname)
	if req.Nickname == "" {
		badRequest(c, fmt.Errorf("nickname must contain letters, numbers, underscore or hyphen"))
		return
	}
	if utf8.RuneCountInString(req.Nickname) < 3 {
		badRequest(c, fmt.Errorf("nickname must contain at least 3 letters or numbers after normalization"))
		return
	}

	hash, err := security.HashPassword(req.Password)
	if err != nil {
		internalServerError(c, err)
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var (
		userID  string
		lastErr error
	)
	for attempt := 0; attempt < 5; attempt++ {
		publicID := generatePublicID()
		lastErr = tx.QueryRow(c.Request.Context(), `
			INSERT INTO users(email, username, first_name, last_name, nickname, public_id, password_hash)
			VALUES($1, $2, $3, $4, $5, $6, $7)
			RETURNING id
		`, req.Email, req.Nickname, req.FirstName, req.LastName, req.Nickname, publicID, hash).Scan(&userID)
		if lastErr == nil {
			break
		}

		var pgErr *pgconn.PgError
		if !errors.As(lastErr, &pgErr) || pgErr.Code != "23505" {
			internalServerError(c, lastErr)
			return
		}
		if strings.Contains(strings.ToLower(pgErr.ConstraintName), "public_id") {
			continue
		}
		if strings.Contains(strings.ToLower(pgErr.ConstraintName), "nickname") ||
			strings.Contains(strings.ToLower(pgErr.ConstraintName), "users_username_key") {
			c.JSON(http.StatusConflict, APIError{Error: "nickname already exists"})
			return
		}
		c.JSON(http.StatusConflict, APIError{Error: "user already exists"})
		return
	}
	if lastErr != nil {
		internalServerError(c, lastErr)
		return
	}

	if _, err := tx.Exec(c.Request.Context(), `
		INSERT INTO user_settings(user_id)
		VALUES ($1)
		ON CONFLICT (user_id) DO NOTHING
	`, userID); err != nil {
		internalServerError(c, err)
		return
	}

	var freePlanID string
	if err := tx.QueryRow(c.Request.Context(), `SELECT id FROM plans WHERE code='free'`).Scan(&freePlanID); err != nil {
		internalServerError(c, err)
		return
	}

	if _, err := tx.Exec(c.Request.Context(), `
		INSERT INTO subscriptions(user_id, plan_id, status)
		VALUES($1, $2, 'active')
		ON CONFLICT DO NOTHING
	`, userID, freePlanID); err != nil {
		internalServerError(c, err)
		return
	}

	verificationToken := uuid.New()
	if _, err := tx.Exec(c.Request.Context(), `
		INSERT INTO email_verifications(token, user_id, expires_at)
		VALUES($1, $2, $3)
	`, verificationToken.String(), userID, time.Now().Add(48*time.Hour)); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	accessToken, refreshToken, err := a.issueTokens(c, userID, "student")
	if err != nil {
		internalServerError(c, err)
		return
	}

	response := gin.H{
		"tokens": tokenResponse{
			AccessToken:     accessToken,
			RefreshToken:    refreshToken,
			AccessTokenTTL:  a.Cfg.JWTAccessTTL.String(),
			RefreshTokenTTL: a.Cfg.JWTRefreshTTL.String(),
			EmailVerified:   false,
			CurrentPlan:     "free",
		},
		"verificationRequired": true,
	}
	if a.Cfg.ExposeDemoTokens {
		response["emailVerificationTokenDemo"] = verificationToken.String()
	}
	c.JSON(http.StatusCreated, response)
}

func (a *App) Login(c *gin.Context) {
	var req loginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	req.Email = normalizeEmail(req.Email)

	var userID, passHash, role, planCode string
	var isBlocked, isVerified bool
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT u.id, u.password_hash, u.role, u.is_blocked, u.is_email_verified, COALESCE(p.code,'free')
		FROM users u
		LEFT JOIN subscriptions s ON s.user_id=u.id AND s.status='active' AND (s.ends_at IS NULL OR s.ends_at > NOW())
		LEFT JOIN plans p ON p.id=s.plan_id
		WHERE u.email=$1
	`, req.Email).Scan(&userID, &passHash, &role, &isBlocked, &isVerified, &planCode)
	if err != nil {
		unauthorized(c, "invalid credentials")
		return
	}

	if isBlocked {
		c.JSON(http.StatusForbidden, APIError{Error: "account blocked"})
		return
	}

	if !security.CheckPassword(passHash, req.Password) {
		unauthorized(c, "invalid credentials")
		return
	}

	accessToken, refreshToken, err := a.issueTokens(c, userID, role)
	if err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, tokenResponse{
		AccessToken:     accessToken,
		RefreshToken:    refreshToken,
		AccessTokenTTL:  a.Cfg.JWTAccessTTL.String(),
		RefreshTokenTTL: a.Cfg.JWTRefreshTTL.String(),
		EmailVerified:   isVerified,
		CurrentPlan:     planCode,
	})
}

func (a *App) RefreshToken(c *gin.Context) {
	var req refreshRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	claims, err := security.ParseToken(req.RefreshToken, a.Cfg.JWTRefreshSecret)
	if err != nil || claims.Type != "refresh" {
		unauthorized(c, "invalid refresh token")
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	var (
		role      string
		isBlocked bool
	)
	if err := tx.QueryRow(c.Request.Context(), `
		SELECT role, is_blocked
		FROM users
		WHERE id = $1
		FOR UPDATE
	`, claims.UserID).Scan(&role, &isBlocked); err != nil {
		unauthorized(c, "refresh session expired")
		return
	}
	if isBlocked {
		c.JSON(http.StatusForbidden, APIError{Error: "account blocked"})
		return
	}

	if err := tx.QueryRow(c.Request.Context(), `
		DELETE FROM refresh_tokens
		WHERE token = $1 AND user_id = $2 AND expires_at > NOW()
		RETURNING token
	`, req.RefreshToken, claims.UserID).Scan(new(string)); err != nil {
		unauthorized(c, "refresh session expired")
		return
	}

	accessToken, err := security.CreateToken(claims.UserID, role, "access", a.Cfg.JWTAccessSecret, a.Cfg.JWTAccessTTL)
	if err != nil {
		internalServerError(c, err)
		return
	}
	refreshToken, err := security.CreateToken(claims.UserID, role, "refresh", a.Cfg.JWTRefreshSecret, a.Cfg.JWTRefreshTTL)
	if err != nil {
		internalServerError(c, err)
		return
	}
	if _, err := tx.Exec(c.Request.Context(), `
		INSERT INTO refresh_tokens(token, user_id, expires_at)
		VALUES($1, $2, NOW() + ($3::int * interval '1 second'))
	`, refreshToken, claims.UserID, int(a.Cfg.JWTRefreshTTL.Seconds())); err != nil {
		internalServerError(c, err)
		return
	}
	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"accessToken":     accessToken,
		"refreshToken":    refreshToken,
		"accessTokenTtl":  a.Cfg.JWTAccessTTL.String(),
		"refreshTokenTtl": a.Cfg.JWTRefreshTTL.String(),
	})
}

func (a *App) VerifyEmail(c *gin.Context) {
	var req struct {
		Token string `json:"token" binding:"required,uuid"`
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

	var userID string
	err = tx.QueryRow(c.Request.Context(), `
		SELECT user_id FROM email_verifications
		WHERE token = $1 AND expires_at > NOW()
	`, req.Token).Scan(&userID)
	if err != nil {
		notFound(c, "verification token not found or expired")
		return
	}

	if _, err := tx.Exec(c.Request.Context(), `UPDATE users SET is_email_verified=TRUE, updated_at=NOW() WHERE id=$1`, userID); err != nil {
		internalServerError(c, err)
		return
	}
	if _, err := tx.Exec(c.Request.Context(), `DELETE FROM email_verifications WHERE token=$1`, req.Token); err != nil {
		internalServerError(c, err)
		return
	}

	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "verified"})
}

func (a *App) ForgotPassword(c *gin.Context) {
	var req struct {
		Email string `json:"email" binding:"required,email"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}
	req.Email = normalizeEmail(req.Email)

	var userID string
	err := a.DB.QueryRow(c.Request.Context(), `SELECT id FROM users WHERE email=$1`, req.Email).Scan(&userID)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
		return
	}

	token := uuid.New().String()
	_, err = a.DB.Exec(c.Request.Context(), `
		INSERT INTO password_resets(token, user_id, expires_at)
		VALUES($1, $2, $3)
	`, token, userID, time.Now().Add(2*time.Hour))
	if err != nil {
		internalServerError(c, err)
		return
	}

	response := gin.H{"status": "ok"}
	if a.Cfg.ExposeDemoTokens {
		response["resetTokenDemo"] = token
		response["hint"] = "SMTP не настроен в демо. Токен возвращается только для тестовой среды."
	}
	c.JSON(http.StatusOK, response)
}

func (a *App) ResetPassword(c *gin.Context) {
	var req struct {
		Token       string `json:"token" binding:"required,uuid"`
		NewPassword string `json:"newPassword" binding:"required,min=8,max=128"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	var userID string
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT user_id FROM password_resets WHERE token=$1 AND expires_at > NOW()
	`, req.Token).Scan(&userID)
	if err != nil {
		notFound(c, "reset token not found or expired")
		return
	}

	hash, err := security.HashPassword(req.NewPassword)
	if err != nil {
		internalServerError(c, err)
		return
	}

	tx, err := a.DB.Begin(c.Request.Context())
	if err != nil {
		internalServerError(c, err)
		return
	}
	defer tx.Rollback(c.Request.Context())

	if _, err := tx.Exec(c.Request.Context(), `UPDATE users SET password_hash=$1, updated_at=NOW() WHERE id=$2`, hash, userID); err != nil {
		internalServerError(c, err)
		return
	}
	if _, err := tx.Exec(c.Request.Context(), `DELETE FROM password_resets WHERE user_id=$1`, userID); err != nil {
		internalServerError(c, err)
		return
	}
	if _, err := tx.Exec(c.Request.Context(), `DELETE FROM refresh_tokens WHERE user_id=$1`, userID); err != nil {
		internalServerError(c, err)
		return
	}
	if err := tx.Commit(c.Request.Context()); err != nil {
		internalServerError(c, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "password_updated"})
}

func (a *App) OAuthStart(c *gin.Context) {
	provider := c.Param("provider")
	c.JSON(http.StatusGone, gin.H{
		"provider": provider,
		"status":   "disabled",
		"message":  "OAuth вход отключен для production запуска. Используйте регистрацию по email.",
	})
}

func (a *App) OAuthCallback(c *gin.Context) {
	c.JSON(http.StatusGone, APIError{Error: "oauth login disabled"})
}

func (a *App) issueTokens(c *gin.Context, userID, role string) (string, string, error) {
	accessToken, err := security.CreateToken(userID, role, "access", a.Cfg.JWTAccessSecret, a.Cfg.JWTAccessTTL)
	if err != nil {
		return "", "", err
	}
	refreshToken, err := security.CreateToken(userID, role, "refresh", a.Cfg.JWTRefreshSecret, a.Cfg.JWTRefreshTTL)
	if err != nil {
		return "", "", err
	}

	if _, err := a.DB.Exec(c.Request.Context(), `
		INSERT INTO refresh_tokens(token, user_id, expires_at)
		VALUES($1, $2, NOW() + ($3::int * interval '1 second'))
	`, refreshToken, userID, int(a.Cfg.JWTRefreshTTL.Seconds())); err != nil {
		return "", "", err
	}

	return accessToken, refreshToken, nil
}

func normalizeNickname(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return ""
	}
	var b strings.Builder
	b.Grow(len(raw))
	for _, r := range raw {
		switch {
		case unicode.IsLetter(r) || unicode.IsNumber(r):
			b.WriteRune(unicode.ToLower(r))
		case r == '_' || r == '-':
			b.WriteRune(r)
		case r == ' ' || r == '.':
			b.WriteRune('_')
		}
	}
	nick := strings.Trim(b.String(), "_-")
	if utf8.RuneCountInString(nick) > 32 {
		runes := []rune(nick)
		nick = string(runes[:32])
	}
	return nick
}

func normalizeEmail(raw string) string {
	return strings.TrimSpace(strings.ToLower(raw))
}

func generatePublicID() string {
	id := strings.ToUpper(strings.ReplaceAll(uuid.NewString(), "-", ""))
	if len(id) < 10 {
		return "LC-" + id
	}
	return "LC-" + id[:10]
}
