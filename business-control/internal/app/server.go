package app

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"business-control/web"
	"golang.org/x/crypto/bcrypt"
)

const sessionCookieName = "business_session"

var usernamePattern = regexp.MustCompile(`^[A-Za-z0-9_]{3,32}$`)

var recordTypes = map[string]struct{}{
	"goal": {}, "task": {}, "idea": {}, "criterion": {}, "research": {},
	"decision": {}, "disagreement": {}, "document": {},
}

var recordStatuses = map[string]struct{}{
	"draft": {}, "inbox": {}, "review": {}, "main": {}, "rejected": {},
	"planned": {}, "in_progress": {}, "blocked": {}, "completed": {},
	"postponed": {}, "cancelled": {}, "archived": {},
}

type Server struct {
	store  *Store
	config Config
	mux    *http.ServeMux
}

type contextKey string

const userContextKey contextKey = "user"

func NewServer(store *Store, config Config) http.Handler {
	server := &Server{store: store, config: config, mux: http.NewServeMux()}
	server.routes()
	return server.securityHeaders(server.mux)
}

func (s *Server) routes() {
	s.mux.HandleFunc("GET /api/health", s.handleHealth)
	s.mux.HandleFunc("POST /api/auth/register", s.handleRegister)
	s.mux.HandleFunc("POST /api/auth/login", s.handleLogin)
	s.mux.Handle("POST /api/auth/logout", s.requireAuth(http.HandlerFunc(s.handleLogout)))
	s.mux.Handle("GET /api/me", s.requireAuth(http.HandlerFunc(s.handleMe)))
	s.mux.Handle("PATCH /api/me", s.requireAuth(http.HandlerFunc(s.handleUpdateMe)))
	s.mux.Handle("GET /api/users", s.requireAuth(http.HandlerFunc(s.handleUsers)))

	s.mux.Handle("GET /api/records", s.requireAuth(http.HandlerFunc(s.handleListRecords)))
	s.mux.Handle("POST /api/records", s.requireAuth(http.HandlerFunc(s.handleCreateRecord)))
	s.mux.Handle("GET /api/records/{id}", s.requireAuth(http.HandlerFunc(s.handleGetRecord)))
	s.mux.Handle("PATCH /api/records/{id}", s.requireAuth(http.HandlerFunc(s.handleUpdateRecord)))
	s.mux.Handle("POST /api/records/{id}/archive", s.requireAuth(http.HandlerFunc(s.handleArchiveRecord)))
	s.mux.Handle("GET /api/records/{id}/sections", s.requireAuth(http.HandlerFunc(s.handleSections)))
	s.mux.Handle("POST /api/records/{id}/sections", s.requireAuth(http.HandlerFunc(s.handleSaveSection)))
	s.mux.Handle("POST /api/records/{id}/links", s.requireAuth(http.HandlerFunc(s.handleCreateLink)))
	s.mux.Handle("POST /api/records/{id}/links/{linkId}/remove", s.requireAuth(http.HandlerFunc(s.handleRemoveLink)))
	s.mux.Handle("PUT /api/records/{id}/criteria/{criterionId}", s.requireAuth(http.HandlerFunc(s.handleScoreCriterion)))
	s.mux.Handle("POST /api/records/{id}/proofs", s.requireAuth(http.HandlerFunc(s.handleAddProof)))
	s.mux.Handle("POST /api/records/{id}/complete", s.requireAuth(http.HandlerFunc(s.handleCompleteTask)))
	s.mux.Handle("POST /api/records/{id}/notify", s.requireAuth(http.HandlerFunc(s.handleNotifyPartners)))

	s.mux.Handle("GET /api/section-definitions", s.requireAuth(http.HandlerFunc(s.handleListDefinitions)))
	s.mux.Handle("POST /api/section-definitions", s.requireAuth(http.HandlerFunc(s.handleCreateDefinition)))
	s.mux.Handle("PATCH /api/section-definitions/{id}", s.requireAuth(http.HandlerFunc(s.handleUpdateDefinition)))
	s.mux.Handle("GET /api/notifications", s.requireAuth(http.HandlerFunc(s.handleNotifications)))
	s.mux.Handle("POST /api/notifications/read-all", s.requireAuth(http.HandlerFunc(s.handleReadAllNotifications)))
	s.mux.Handle("POST /api/notifications/{id}/read", s.requireAuth(http.HandlerFunc(s.handleReadNotification)))
	s.mux.Handle("GET /api/activity", s.requireAuth(http.HandlerFunc(s.handleActivity)))

	s.mux.Handle("GET /", http.FileServer(http.FS(web.Files)))
}

func (s *Server) securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Referrer-Policy", "same-origin")
		w.Header().Set("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
		next.ServeHTTP(w, r)
	})
}

func (s *Server) requireAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		cookie, err := r.Cookie(sessionCookieName)
		if err != nil || strings.TrimSpace(cookie.Value) == "" {
			writeError(w, http.StatusUnauthorized, "Нужен вход в аккаунт")
			return
		}
		var user User
		err = s.store.db.QueryRowContext(r.Context(), `
			SELECT u.id, u.email, u.username, u.created_at
			FROM sessions s JOIN users u ON u.id = s.user_id
			WHERE s.token_hash = ? AND s.expires_at > ?`, hashToken(cookie.Value), nowText()).
			Scan(&user.ID, &user.Email, &user.Username, &user.CreatedAt)
		if errors.Is(err, sql.ErrNoRows) {
			s.clearSessionCookie(w)
			writeError(w, http.StatusUnauthorized, "Сессия истекла")
			return
		}
		if err != nil {
			log.Printf("authenticate: %v", err)
			writeError(w, http.StatusInternalServerError, "Не удалось проверить сессию")
			return
		}
		_, _ = s.store.db.ExecContext(r.Context(), `UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?`, nowText(), hashToken(cookie.Value))
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), userContextKey, user)))
	})
}

func currentUser(r *http.Request) User {
	return r.Context().Value(userContextKey).(User)
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	if err := s.store.db.PingContext(r.Context()); err != nil {
		writeError(w, http.StatusServiceUnavailable, "database unavailable")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok"})
}

type registerRequest struct {
	Email    string `json:"email"`
	Username string `json:"username"`
	Password string `json:"password"`
}

func (s *Server) handleRegister(w http.ResponseWriter, r *http.Request) {
	var input registerRequest
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Email = strings.ToLower(strings.TrimSpace(input.Email))
	input.Username = strings.TrimSpace(input.Username)
	if !strings.Contains(input.Email, "@") || len(input.Email) > 254 {
		writeError(w, http.StatusBadRequest, "Укажите корректную почту")
		return
	}
	if !usernamePattern.MatchString(input.Username) {
		writeError(w, http.StatusBadRequest, "Логин: 3–32 символа, латинские буквы, цифры и _")
		return
	}
	if len(input.Password) < 8 || len(input.Password) > 128 {
		writeError(w, http.StatusBadRequest, "Пароль должен содержать от 8 до 128 символов")
		return
	}
	if len(s.config.AllowedUsernames) > 0 {
		if _, ok := s.config.AllowedUsernames[strings.ToLower(input.Username)]; !ok {
			writeError(w, http.StatusForbidden, "Этот логин не входит в рабочую команду")
			return
		}
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(input.Password), bcrypt.DefaultCost)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось создать пароль")
		return
	}
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать регистрацию")
		return
	}
	defer tx.Rollback()
	now := nowText()
	result, err := tx.ExecContext(r.Context(), `INSERT INTO users(email, username, password_hash, created_at, updated_at) VALUES(?, ?, ?, ?, ?)`, input.Email, input.Username, string(hash), now, now)
	if err != nil {
		if strings.Contains(strings.ToLower(err.Error()), "unique") {
			writeError(w, http.StatusConflict, "Почта или логин уже заняты")
			return
		}
		log.Printf("register user: %v", err)
		writeError(w, http.StatusInternalServerError, "Не удалось зарегистрироваться")
		return
	}
	userID, _ := result.LastInsertId()
	if err := writeActivity(r.Context(), tx, userID, "user", strconv.FormatInt(userID, 10), "created", "", map[string]any{"username": input.Username}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать регистрацию")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить регистрацию")
		return
	}
	user := User{ID: userID, Email: input.Email, Username: input.Username, CreatedAt: now}
	if err := s.createSession(w, r, user.ID); err != nil {
		writeError(w, http.StatusInternalServerError, "Аккаунт создан, но вход не выполнен")
		return
	}
	writeJSON(w, http.StatusCreated, user)
}

type loginRequest struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

func (s *Server) handleLogin(w http.ResponseWriter, r *http.Request) {
	var input loginRequest
	if !decodeJSON(w, r, &input) {
		return
	}
	var user User
	var passwordHash string
	err := s.store.db.QueryRowContext(r.Context(), `SELECT id, email, username, created_at, password_hash FROM users WHERE email = ? OR username = ?`, strings.TrimSpace(input.Login), strings.TrimSpace(input.Login)).
		Scan(&user.ID, &user.Email, &user.Username, &user.CreatedAt, &passwordHash)
	if err != nil || bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte(input.Password)) != nil {
		writeError(w, http.StatusUnauthorized, "Неверный логин или пароль")
		return
	}
	if err := s.createSession(w, r, user.ID); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось создать сессию")
		return
	}
	writeJSON(w, http.StatusOK, user)
}

func (s *Server) createSession(w http.ResponseWriter, r *http.Request, userID int64) error {
	token, tokenHash, err := newSessionToken()
	if err != nil {
		return err
	}
	now := time.Now().UTC()
	expires := now.Add(s.config.SessionLifetime)
	_, err = s.store.db.ExecContext(r.Context(), `INSERT INTO sessions(user_id, token_hash, expires_at, created_at, last_seen_at) VALUES(?, ?, ?, ?, ?)`, userID, tokenHash, expires.Format(time.RFC3339Nano), now.Format(time.RFC3339Nano), now.Format(time.RFC3339Nano))
	if err != nil {
		return err
	}
	http.SetCookie(w, &http.Cookie{Name: sessionCookieName, Value: token, Path: "/", HttpOnly: true, Secure: s.config.CookieSecure, SameSite: http.SameSiteLaxMode, Expires: expires, MaxAge: int(s.config.SessionLifetime.Seconds())})
	return nil
}

func (s *Server) clearSessionCookie(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{Name: sessionCookieName, Value: "", Path: "/", HttpOnly: true, Secure: s.config.CookieSecure, SameSite: http.SameSiteLaxMode, MaxAge: -1, Expires: time.Unix(0, 0)})
}

func (s *Server) handleLogout(w http.ResponseWriter, r *http.Request) {
	if cookie, err := r.Cookie(sessionCookieName); err == nil {
		_, _ = s.store.db.ExecContext(r.Context(), `DELETE FROM sessions WHERE token_hash = ?`, hashToken(cookie.Value))
	}
	s.clearSessionCookie(w)
	w.WriteHeader(http.StatusNoContent)
}

func (s *Server) handleMe(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, currentUser(r))
}

func (s *Server) handleUpdateMe(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Username string `json:"username"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Username = strings.TrimSpace(input.Username)
	if !usernamePattern.MatchString(input.Username) {
		writeError(w, http.StatusBadRequest, "Логин: 3–32 символа, латинские буквы, цифры и _")
		return
	}
	if len(s.config.AllowedUsernames) > 0 {
		if _, ok := s.config.AllowedUsernames[strings.ToLower(input.Username)]; !ok {
			writeError(w, http.StatusForbidden, "Новый логин нужно сначала добавить в конфигурацию команды")
			return
		}
	}
	user := currentUser(r)
	beforeUsername := user.Username
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать изменение профиля")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `UPDATE users SET username = ?, updated_at = ? WHERE id = ?`, input.Username, nowText(), user.ID); err != nil {
		writeError(w, http.StatusConflict, "Логин уже занят")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, "user", strconv.FormatInt(user.ID, 10), "profile_updated", "", map[string]any{
		"username": map[string]any{"before": beforeUsername, "after": input.Username},
	}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю профиля")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить изменение профиля")
		return
	}
	user.Username = input.Username
	writeJSON(w, http.StatusOK, user)
}

func (s *Server) handleUsers(w http.ResponseWriter, r *http.Request) {
	rows, err := s.store.db.QueryContext(r.Context(), `SELECT id, email, username, created_at FROM users ORDER BY username`)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить участников")
		return
	}
	defer rows.Close()
	users := make([]User, 0)
	for rows.Next() {
		var user User
		if err := rows.Scan(&user.ID, &user.Email, &user.Username, &user.CreatedAt); err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось прочитать участников")
			return
		}
		users = append(users, user)
	}
	writeJSON(w, http.StatusOK, users)
}

type recordScanner interface{ Scan(...any) error }

const recordSelect = `
	SELECT r.id, r.type, r.title, r.description, r.status,
		r.author_id, author.username, r.owner_id, owner.username,
		r.decision_maker_id, decision_maker.username, r.due_at,
		r.estimate_minutes, r.progress, r.progress_note, r.result, r.completed_at,
		r.created_at, r.updated_at,
		(SELECT COUNT(*) FROM task_proofs p WHERE p.record_id = r.id)
	FROM records r
	JOIN users author ON author.id = r.author_id
	JOIN users owner ON owner.id = r.owner_id
	LEFT JOIN users decision_maker ON decision_maker.id = r.decision_maker_id`

func scanRecord(scanner recordScanner) (Record, error) {
	var record Record
	var decisionMakerID sql.NullInt64
	var decisionMakerName, dueAt, completedAt sql.NullString
	err := scanner.Scan(&record.ID, &record.Type, &record.Title, &record.Description, &record.Status,
		&record.AuthorID, &record.AuthorUsername, &record.OwnerID, &record.OwnerUsername,
		&decisionMakerID, &decisionMakerName, &dueAt, &record.EstimateMinutes, &record.Progress,
		&record.ProgressNote, &record.Result, &completedAt, &record.CreatedAt, &record.UpdatedAt, &record.ProofCount)
	if decisionMakerID.Valid {
		record.DecisionMakerID = &decisionMakerID.Int64
	}
	if decisionMakerName.Valid {
		record.DecisionMakerName = &decisionMakerName.String
	}
	if dueAt.Valid {
		record.DueAt = &dueAt.String
	}
	if completedAt.Valid {
		record.CompletedAt = &completedAt.String
	}
	return record, err
}

func (s *Server) getRecord(ctx context.Context, id string) (Record, error) {
	return scanRecord(s.store.db.QueryRowContext(ctx, recordSelect+` WHERE r.id = ?`, id))
}

func (s *Server) handleListRecords(w http.ResponseWriter, r *http.Request) {
	where := []string{"1 = 1"}
	args := make([]any, 0)
	if recordType := strings.TrimSpace(r.URL.Query().Get("type")); recordType != "" {
		if _, ok := recordTypes[recordType]; !ok {
			writeError(w, http.StatusBadRequest, "Неизвестный тип карточки")
			return
		}
		where = append(where, "r.type = ?")
		args = append(args, recordType)
	}
	if status := strings.TrimSpace(r.URL.Query().Get("status")); status != "" {
		if _, ok := recordStatuses[status]; !ok {
			writeError(w, http.StatusBadRequest, "Неизвестный статус")
			return
		}
		where = append(where, "r.status = ?")
		args = append(args, status)
	} else if r.URL.Query().Get("includeArchived") != "true" {
		where = append(where, "r.status <> 'archived'")
	}
	if owner := strings.TrimSpace(r.URL.Query().Get("ownerId")); owner != "" {
		ownerID, err := strconv.ParseInt(owner, 10, 64)
		if err != nil {
			writeError(w, http.StatusBadRequest, "Некорректный владелец")
			return
		}
		where = append(where, "r.owner_id = ?")
		args = append(args, ownerID)
	}
	if search := strings.TrimSpace(r.URL.Query().Get("search")); search != "" {
		where = append(where, "(r.title LIKE ? OR r.description LIKE ?)")
		args = append(args, "%"+search+"%", "%"+search+"%")
	}
	query := recordSelect + " WHERE " + strings.Join(where, " AND ") + " ORDER BY CASE WHEN r.due_at IS NULL THEN 1 ELSE 0 END, r.due_at, r.updated_at DESC LIMIT 500"
	rows, err := s.store.db.QueryContext(r.Context(), query, args...)
	if err != nil {
		log.Printf("list records: %v", err)
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточки")
		return
	}
	defer rows.Close()
	records := make([]Record, 0)
	for rows.Next() {
		record, err := scanRecord(rows)
		if err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось прочитать карточки")
			return
		}
		records = append(records, record)
	}
	writeJSON(w, http.StatusOK, records)
}

type createRecordRequest struct {
	Type            string `json:"type"`
	Title           string `json:"title"`
	Description     string `json:"description"`
	Status          string `json:"status"`
	OwnerID         int64  `json:"ownerId"`
	DecisionMakerID *int64 `json:"decisionMakerId"`
	DueAt           string `json:"dueAt"`
	EstimateMinutes int    `json:"estimateMinutes"`
}

func defaultStatus(recordType string) string {
	switch recordType {
	case "idea":
		return "inbox"
	case "goal", "task":
		return "planned"
	default:
		return "draft"
	}
}

func validStatusForType(recordType, status string) bool {
	if status == "archived" {
		return true
	}
	switch recordType {
	case "idea":
		return status == "inbox" || status == "review" || status == "main" || status == "rejected"
	case "goal", "task":
		return status == "planned" || status == "in_progress" || status == "blocked" || status == "completed" || status == "postponed" || status == "cancelled"
	default:
		return status == "draft" || status == "in_progress" || status == "completed" || status == "cancelled"
	}
}

func (s *Server) handleCreateRecord(w http.ResponseWriter, r *http.Request) {
	var input createRecordRequest
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Type = strings.TrimSpace(input.Type)
	input.Title = strings.TrimSpace(input.Title)
	if _, ok := recordTypes[input.Type]; !ok {
		writeError(w, http.StatusBadRequest, "Неизвестный тип карточки")
		return
	}
	if input.Title == "" || len(input.Title) > 240 {
		writeError(w, http.StatusBadRequest, "Название обязательно и не длиннее 240 символов")
		return
	}
	if input.Status == "" {
		input.Status = defaultStatus(input.Type)
	}
	if !validStatusForType(input.Type, input.Status) || input.Status == "completed" || input.Status == "archived" {
		writeError(w, http.StatusBadRequest, "Некорректный начальный статус")
		return
	}
	user := currentUser(r)
	if input.OwnerID == 0 {
		input.OwnerID = user.ID
	}
	if !s.userExists(r.Context(), input.OwnerID) || (input.DecisionMakerID != nil && !s.userExists(r.Context(), *input.DecisionMakerID)) {
		writeError(w, http.StatusBadRequest, "Указанный участник не найден")
		return
	}
	if input.EstimateMinutes < 0 || input.EstimateMinutes > 525600 {
		writeError(w, http.StatusBadRequest, "Некорректная оценка времени")
		return
	}
	dueAt, err := normalizeDueAt(input.DueAt)
	if err != nil {
		writeError(w, http.StatusBadRequest, "Некорректный срок")
		return
	}
	id, err := newID()
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось создать идентификатор")
		return
	}
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать создание")
		return
	}
	defer tx.Rollback()
	now := nowText()
	_, err = tx.ExecContext(r.Context(), `INSERT INTO records(id, type, title, description, status, author_id, owner_id, decision_maker_id, due_at, estimate_minutes, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`, id, input.Type, input.Title, strings.TrimSpace(input.Description), input.Status, user.ID, input.OwnerID, input.DecisionMakerID, dueAt, input.EstimateMinutes, now, now)
	if err != nil {
		log.Printf("create record: %v", err)
		writeError(w, http.StatusInternalServerError, "Не удалось создать карточку")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, input.Type, id, "created", "", map[string]any{"title": input.Title, "status": input.Status, "ownerId": input.OwnerID}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить создание")
		return
	}
	record, _ := s.getRecord(r.Context(), id)
	writeJSON(w, http.StatusCreated, record)
}

func (s *Server) handleGetRecord(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточку")
		return
	}
	sections, _ := s.listSections(r.Context(), record)
	links, _ := s.listLinks(r.Context(), record.ID)
	scores, _ := s.listScores(r.Context(), record.ID)
	proofs, _ := s.listProofs(r.Context(), record.ID)
	writeJSON(w, http.StatusOK, map[string]any{"record": record, "sections": sections, "links": links, "scores": scores, "proofs": proofs})
}

type updateRecordRequest struct {
	Title              *string `json:"title"`
	Description        *string `json:"description"`
	Status             *string `json:"status"`
	OwnerID            *int64  `json:"ownerId"`
	DecisionMakerID    *int64  `json:"decisionMakerId"`
	ClearDecisionMaker bool    `json:"clearDecisionMaker"`
	DueAt              *string `json:"dueAt"`
	EstimateMinutes    *int    `json:"estimateMinutes"`
	Progress           *int    `json:"progress"`
	ProgressNote       *string `json:"progressNote"`
	Result             *string `json:"result"`
	Reason             string  `json:"reason"`
}

func (s *Server) handleUpdateRecord(w http.ResponseWriter, r *http.Request) {
	before, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточку")
		return
	}
	var input updateRecordRequest
	if !decodeJSON(w, r, &input) {
		return
	}
	if (input.Status != nil || input.DueAt != nil) && strings.TrimSpace(input.Reason) == "" {
		writeError(w, http.StatusBadRequest, "Укажите причину изменения статуса или срока")
		return
	}
	updates := make([]string, 0)
	args := make([]any, 0)
	changes := make(map[string]any)
	add := func(column string, value any) { updates = append(updates, column+" = ?"); args = append(args, value) }
	if input.Title != nil {
		value := strings.TrimSpace(*input.Title)
		if value == "" || len(value) > 240 {
			writeError(w, http.StatusBadRequest, "Некорректное название")
			return
		}
		add("title", value)
		changes["title"] = map[string]any{"before": before.Title, "after": value}
	}
	if input.Description != nil {
		value := strings.TrimSpace(*input.Description)
		add("description", value)
		changes["description"] = map[string]any{"before": before.Description, "after": value}
	}
	if input.Status != nil {
		if !validStatusForType(before.Type, *input.Status) {
			writeError(w, http.StatusBadRequest, "Статус не подходит типу карточки")
			return
		}
		if before.Type == "task" && *input.Status == "completed" {
			writeError(w, http.StatusBadRequest, "Задача завершается только с доказательством")
			return
		}
		add("status", *input.Status)
		changes["status"] = map[string]any{"before": before.Status, "after": *input.Status}
		if *input.Status == "archived" {
			add("archived_at", nowText())
		}
		if *input.Status == "completed" {
			add("completed_at", nowText())
			add("progress", 100)
		}
	}
	if input.OwnerID != nil {
		if !s.userExists(r.Context(), *input.OwnerID) {
			writeError(w, http.StatusBadRequest, "Ответственный не найден")
			return
		}
		add("owner_id", *input.OwnerID)
		changes["ownerId"] = map[string]any{"before": before.OwnerID, "after": *input.OwnerID}
	}
	if input.DecisionMakerID != nil {
		if !s.userExists(r.Context(), *input.DecisionMakerID) {
			writeError(w, http.StatusBadRequest, "Участник не найден")
			return
		}
		add("decision_maker_id", *input.DecisionMakerID)
		changes["decisionMakerId"] = map[string]any{"before": before.DecisionMakerID, "after": *input.DecisionMakerID}
	} else if input.ClearDecisionMaker {
		add("decision_maker_id", nil)
		changes["decisionMakerId"] = map[string]any{"before": before.DecisionMakerID, "after": nil}
	}
	if input.DueAt != nil {
		dueAt, err := normalizeDueAt(*input.DueAt)
		if err != nil {
			writeError(w, http.StatusBadRequest, "Некорректный срок")
			return
		}
		add("due_at", dueAt)
		changes["dueAt"] = map[string]any{"before": before.DueAt, "after": dueAt}
	}
	if input.EstimateMinutes != nil {
		if *input.EstimateMinutes < 0 || *input.EstimateMinutes > 525600 {
			writeError(w, http.StatusBadRequest, "Некорректная оценка времени")
			return
		}
		add("estimate_minutes", *input.EstimateMinutes)
		changes["estimateMinutes"] = map[string]any{"before": before.EstimateMinutes, "after": *input.EstimateMinutes}
	}
	if input.Progress != nil {
		if *input.Progress < 0 || *input.Progress > 100 {
			writeError(w, http.StatusBadRequest, "Прогресс должен быть от 0 до 100")
			return
		}
		add("progress", *input.Progress)
		changes["progress"] = map[string]any{"before": before.Progress, "after": *input.Progress}
		if input.Status == nil && before.Status == "planned" && *input.Progress > 0 {
			add("status", "in_progress")
			changes["status"] = map[string]any{"before": before.Status, "after": "in_progress"}
		}
	}
	if input.ProgressNote != nil {
		value := strings.TrimSpace(*input.ProgressNote)
		add("progress_note", value)
		changes["progressNote"] = map[string]any{"before": before.ProgressNote, "after": value}
	}
	if input.Result != nil {
		value := strings.TrimSpace(*input.Result)
		add("result", value)
		changes["result"] = map[string]any{"before": before.Result, "after": value}
	}
	if len(updates) == 0 {
		writeError(w, http.StatusBadRequest, "Нет изменений")
		return
	}
	add("updated_at", nowText())
	args = append(args, before.ID)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать изменение")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `UPDATE records SET `+strings.Join(updates, ", ")+` WHERE id = ?`, args...); err != nil {
		log.Printf("update record: %v", err)
		writeError(w, http.StatusInternalServerError, "Не удалось сохранить карточку")
		return
	}
	user := currentUser(r)
	if err := writeActivity(r.Context(), tx, user.ID, before.Type, before.ID, "updated", strings.TrimSpace(input.Reason), changes); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить изменение")
		return
	}
	after, _ := s.getRecord(r.Context(), before.ID)
	writeJSON(w, http.StatusOK, after)
}

func (s *Server) handleArchiveRecord(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Reason string `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	if strings.TrimSpace(input.Reason) == "" {
		writeError(w, http.StatusBadRequest, "Укажите причину архивации")
		return
	}
	status := "archived"
	s.handleUpdateRecordWithInput(w, r, updateRecordRequest{Status: &status, Reason: input.Reason})
}

func (s *Server) handleUpdateRecordWithInput(w http.ResponseWriter, r *http.Request, input updateRecordRequest) {
	// Archive is intentionally implemented explicitly because request bodies can only be decoded once.
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточку")
		return
	}
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать архивацию")
		return
	}
	defer tx.Rollback()
	now := nowText()
	if _, err := tx.ExecContext(r.Context(), `UPDATE records SET status = 'archived', archived_at = ?, updated_at = ? WHERE id = ?`, now, now, record.ID); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось архивировать карточку")
		return
	}
	user := currentUser(r)
	if err := writeActivity(r.Context(), tx, user.ID, record.Type, record.ID, "archived", input.Reason, map[string]any{"status": map[string]any{"before": record.Status, "after": "archived"}}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить архивацию")
		return
	}
	archived, _ := s.getRecord(r.Context(), record.ID)
	writeJSON(w, http.StatusOK, archived)
}

func (s *Server) userExists(ctx context.Context, id int64) bool {
	var count int
	return s.store.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM users WHERE id = ?`, id).Scan(&count) == nil && count == 1
}

func (s *Server) listSections(ctx context.Context, record Record) ([]RecordSection, error) {
	rows, err := s.store.db.QueryContext(ctx, `
		SELECT COALESCE(rs.id, ''), rs.record_id, d.id, d.name, COALESCE(rs.content, ''), d.sort_order,
			COALESCE(rs.updated_by, 0), COALESCE(u.username, ''), COALESCE(rs.updated_at, d.updated_at)
		FROM section_definitions d
		LEFT JOIN record_sections rs ON rs.definition_id = d.id AND rs.record_id = ?
		LEFT JOIN users u ON u.id = rs.updated_by
		WHERE (d.scope_type IS NULL OR d.scope_type = ?) AND (d.active = 1 OR rs.id IS NOT NULL)
		UNION ALL
		SELECT rs.id, rs.record_id, NULL, rs.title, rs.content, rs.sort_order, rs.updated_by, u.username, rs.updated_at
		FROM record_sections rs JOIN users u ON u.id = rs.updated_by
		WHERE rs.record_id = ? AND rs.definition_id IS NULL
		ORDER BY 6, 9`, record.ID, record.Type, record.ID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	sections := make([]RecordSection, 0)
	for rows.Next() {
		var section RecordSection
		var recordID, definitionID sql.NullString
		if err := rows.Scan(&section.ID, &recordID, &definitionID, &section.Title, &section.Content, &section.SortOrder, &section.UpdatedBy, &section.UpdatedByName, &section.UpdatedAt); err != nil {
			return nil, err
		}
		section.RecordID = record.ID
		if definitionID.Valid {
			section.DefinitionID = &definitionID.String
		}
		sections = append(sections, section)
	}
	return sections, rows.Err()
}

func (s *Server) handleSections(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточку")
		return
	}
	sections, err := s.listSections(r.Context(), record)
	if err != nil {
		log.Printf("list sections: %v", err)
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить разделы")
		return
	}
	writeJSON(w, http.StatusOK, sections)
}

func (s *Server) handleSaveSection(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить карточку")
		return
	}
	var input struct {
		DefinitionID *string `json:"definitionId"`
		SectionID    string  `json:"sectionId"`
		Title        string  `json:"title"`
		Content      string  `json:"content"`
		Reason       string  `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Title = strings.TrimSpace(input.Title)
	input.Content = strings.TrimSpace(input.Content)
	if input.DefinitionID == nil && input.Title == "" {
		writeError(w, http.StatusBadRequest, "Укажите название раздела")
		return
	}
	user := currentUser(r)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать сохранение")
		return
	}
	defer tx.Rollback()
	now := nowText()
	sectionID := strings.TrimSpace(input.SectionID)
	before := ""
	if input.DefinitionID != nil {
		var definitionName, scope sql.NullString
		if err := tx.QueryRowContext(r.Context(), `SELECT name, scope_type FROM section_definitions WHERE id = ?`, *input.DefinitionID).Scan(&definitionName, &scope); err != nil {
			writeError(w, http.StatusBadRequest, "Раздел не найден")
			return
		}
		if scope.Valid && scope.String != record.Type {
			writeError(w, http.StatusBadRequest, "Раздел не подходит типу карточки")
			return
		}
		input.Title = definitionName.String
		err := tx.QueryRowContext(r.Context(), `SELECT id, content FROM record_sections WHERE record_id = ? AND definition_id = ?`, record.ID, *input.DefinitionID).Scan(&sectionID, &before)
		if errors.Is(err, sql.ErrNoRows) {
			sectionID, _ = newID()
			_, err = tx.ExecContext(r.Context(), `INSERT INTO record_sections(id, record_id, definition_id, title, content, sort_order, created_by, updated_by, created_at, updated_at) SELECT ?, ?, id, name, ?, sort_order, ?, ?, ?, ? FROM section_definitions WHERE id = ?`, sectionID, record.ID, input.Content, user.ID, user.ID, now, now, *input.DefinitionID)
		} else if err == nil {
			_, err = tx.ExecContext(r.Context(), `UPDATE record_sections SET content = ?, updated_by = ?, updated_at = ? WHERE id = ?`, input.Content, user.ID, now, sectionID)
		}
		if err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось сохранить раздел")
			return
		}
	} else {
		if sectionID == "" {
			sectionID, _ = newID()
			var sortOrder int
			_ = tx.QueryRowContext(r.Context(), `SELECT COALESCE(MAX(sort_order), 0) + 10 FROM record_sections WHERE record_id = ?`, record.ID).Scan(&sortOrder)
			_, err = tx.ExecContext(r.Context(), `INSERT INTO record_sections(id, record_id, title, content, sort_order, created_by, updated_by, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)`, sectionID, record.ID, input.Title, input.Content, sortOrder, user.ID, user.ID, now, now)
		} else {
			if err := tx.QueryRowContext(r.Context(), `SELECT content FROM record_sections WHERE id = ? AND record_id = ? AND definition_id IS NULL`, sectionID, record.ID).Scan(&before); err != nil {
				writeError(w, http.StatusNotFound, "Раздел не найден")
				return
			}
			_, err = tx.ExecContext(r.Context(), `UPDATE record_sections SET title = ?, content = ?, updated_by = ?, updated_at = ? WHERE id = ?`, input.Title, input.Content, user.ID, now, sectionID)
		}
		if err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось сохранить раздел")
			return
		}
	}
	if err := writeActivity(r.Context(), tx, user.ID, record.Type, record.ID, "section_updated", input.Reason, map[string]any{"sectionId": sectionID, "section": input.Title, "before": before, "after": input.Content}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить сохранение")
		return
	}
	sections, _ := s.listSections(r.Context(), record)
	writeJSON(w, http.StatusOK, sections)
}

func (s *Server) listLinks(ctx context.Context, recordID string) ([]RecordLink, error) {
	rows, err := s.store.db.QueryContext(ctx, `SELECT l.id, l.source_id, l.target_id, l.relation_type, l.created_at, r.id, r.type, r.title, r.description, r.status, r.author_id, a.username, r.owner_id, o.username, r.decision_maker_id, dm.username, r.due_at, r.estimate_minutes, r.progress, r.progress_note, r.result, r.completed_at, r.created_at, r.updated_at, (SELECT COUNT(*) FROM task_proofs p WHERE p.record_id = r.id) FROM record_links l JOIN records r ON r.id = CASE WHEN l.source_id = ? THEN l.target_id ELSE l.source_id END JOIN users a ON a.id = r.author_id JOIN users o ON o.id = r.owner_id LEFT JOIN users dm ON dm.id = r.decision_maker_id WHERE l.active = 1 AND (l.source_id = ? OR l.target_id = ?) ORDER BY l.created_at DESC`, recordID, recordID, recordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	links := make([]RecordLink, 0)
	for rows.Next() {
		var link RecordLink
		var dmID sql.NullInt64
		var dmName, dueAt, completedAt sql.NullString
		if err := rows.Scan(&link.ID, &link.SourceID, &link.TargetID, &link.RelationType, &link.CreatedAt, &link.Record.ID, &link.Record.Type, &link.Record.Title, &link.Record.Description, &link.Record.Status, &link.Record.AuthorID, &link.Record.AuthorUsername, &link.Record.OwnerID, &link.Record.OwnerUsername, &dmID, &dmName, &dueAt, &link.Record.EstimateMinutes, &link.Record.Progress, &link.Record.ProgressNote, &link.Record.Result, &completedAt, &link.Record.CreatedAt, &link.Record.UpdatedAt, &link.Record.ProofCount); err != nil {
			return nil, err
		}
		if dmID.Valid {
			link.Record.DecisionMakerID = &dmID.Int64
		}
		if dmName.Valid {
			link.Record.DecisionMakerName = &dmName.String
		}
		if dueAt.Valid {
			link.Record.DueAt = &dueAt.String
		}
		if completedAt.Valid {
			link.Record.CompletedAt = &completedAt.String
		}
		links = append(links, link)
	}
	return links, rows.Err()
}

func (s *Server) handleCreateLink(w http.ResponseWriter, r *http.Request) {
	source, err := s.getRecord(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	var input struct {
		TargetID     string `json:"targetId"`
		RelationType string `json:"relationType"`
		Reason       string `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	if input.TargetID == source.ID {
		writeError(w, http.StatusBadRequest, "Нельзя связать карточку с самой собой")
		return
	}
	if _, err := s.getRecord(r.Context(), input.TargetID); err != nil {
		writeError(w, http.StatusBadRequest, "Связанная карточка не найдена")
		return
	}
	input.RelationType = strings.TrimSpace(input.RelationType)
	if input.RelationType == "" {
		input.RelationType = "related"
	}
	if len(input.RelationType) > 64 {
		writeError(w, http.StatusBadRequest, "Тип связи слишком длинный")
		return
	}
	id, _ := newID()
	user := currentUser(r)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать создание связи")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `INSERT INTO record_links(id, source_id, target_id, relation_type, created_by, created_at) VALUES(?, ?, ?, ?, ?, ?)`, id, source.ID, input.TargetID, input.RelationType, user.ID, nowText()); err != nil {
		if strings.Contains(strings.ToLower(err.Error()), "unique") {
			writeError(w, http.StatusConflict, "Такая связь уже существует")
		} else {
			writeError(w, http.StatusInternalServerError, "Не удалось создать связь")
		}
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, source.Type, source.ID, "link_created", input.Reason, map[string]any{"targetId": input.TargetID, "relationType": input.RelationType}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить создание связи")
		return
	}
	links, _ := s.listLinks(r.Context(), source.ID)
	writeJSON(w, http.StatusCreated, links)
}

func (s *Server) handleRemoveLink(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if err != nil {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	var input struct {
		Reason string `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	if strings.TrimSpace(input.Reason) == "" {
		writeError(w, http.StatusBadRequest, "Укажите причину удаления связи")
		return
	}
	user := currentUser(r)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать изменение")
		return
	}
	defer tx.Rollback()
	result, err := tx.ExecContext(r.Context(), `UPDATE record_links SET active = 0, removed_by = ?, removed_at = ? WHERE id = ? AND active = 1 AND (source_id = ? OR target_id = ?)`, user.ID, nowText(), r.PathValue("linkId"), record.ID, record.ID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось удалить связь")
		return
	}
	affected, _ := result.RowsAffected()
	if affected == 0 {
		writeError(w, http.StatusNotFound, "Связь не найдена")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, record.Type, record.ID, "link_removed", input.Reason, map[string]any{"linkId": r.PathValue("linkId")}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить изменение")
		return
	}
	links, _ := s.listLinks(r.Context(), record.ID)
	writeJSON(w, http.StatusOK, links)
}

func (s *Server) listScores(ctx context.Context, recordID string) ([]CriterionScore, error) {
	rows, err := s.store.db.QueryContext(ctx, `SELECT cs.id, cs.record_id, cs.criterion_id, c.title, cs.score, cs.note, cs.evaluated_by, u.username, cs.updated_at FROM criterion_scores cs JOIN records c ON c.id = cs.criterion_id JOIN users u ON u.id = cs.evaluated_by WHERE cs.record_id = ? ORDER BY c.title`, recordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	scores := make([]CriterionScore, 0)
	for rows.Next() {
		var score CriterionScore
		if err := rows.Scan(&score.ID, &score.RecordID, &score.CriterionID, &score.CriterionTitle, &score.Score, &score.Note, &score.EvaluatedBy, &score.EvaluatorUsername, &score.UpdatedAt); err != nil {
			return nil, err
		}
		scores = append(scores, score)
	}
	return scores, rows.Err()
}

func (s *Server) handleScoreCriterion(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if err != nil {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	criterion, err := s.getRecord(r.Context(), r.PathValue("criterionId"))
	if err != nil || criterion.Type != "criterion" {
		writeError(w, http.StatusBadRequest, "Критерий не найден")
		return
	}
	var input struct {
		Score  int    `json:"score"`
		Note   string `json:"note"`
		Reason string `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	if input.Score < 0 || input.Score > 10 {
		writeError(w, http.StatusBadRequest, "Оценка должна быть от 0 до 10")
		return
	}
	user := currentUser(r)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать оценку")
		return
	}
	defer tx.Rollback()
	now := nowText()
	id, _ := newID()
	_, err = tx.ExecContext(r.Context(), `INSERT INTO criterion_scores(id, record_id, criterion_id, score, note, evaluated_by, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(record_id, criterion_id) DO UPDATE SET score = excluded.score, note = excluded.note, evaluated_by = excluded.evaluated_by, updated_at = excluded.updated_at`, id, record.ID, criterion.ID, input.Score, strings.TrimSpace(input.Note), user.ID, now, now)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось сохранить оценку")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, record.Type, record.ID, "criterion_scored", input.Reason, map[string]any{"criterionId": criterion.ID, "criterion": criterion.Title, "score": input.Score, "note": input.Note}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить оценку")
		return
	}
	scores, _ := s.listScores(r.Context(), record.ID)
	writeJSON(w, http.StatusOK, scores)
}

func (s *Server) listProofs(ctx context.Context, recordID string) ([]Proof, error) {
	rows, err := s.store.db.QueryContext(ctx, `SELECT p.id, p.record_id, p.author_id, u.username, p.kind, p.content, p.created_at FROM task_proofs p JOIN users u ON u.id = p.author_id WHERE p.record_id = ? ORDER BY p.created_at DESC`, recordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	proofs := make([]Proof, 0)
	for rows.Next() {
		var proof Proof
		if err := rows.Scan(&proof.ID, &proof.RecordID, &proof.AuthorID, &proof.AuthorUsername, &proof.Kind, &proof.Content, &proof.CreatedAt); err != nil {
			return nil, err
		}
		proofs = append(proofs, proof)
	}
	return proofs, rows.Err()
}

func (s *Server) handleAddProof(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if err != nil || record.Type != "task" {
		writeError(w, http.StatusNotFound, "Задача не найдена")
		return
	}
	user := currentUser(r)
	if record.OwnerID != user.ID {
		writeError(w, http.StatusForbidden, "Доказательство добавляет ответственный за задачу")
		return
	}
	var input struct {
		Kind    string `json:"kind"`
		Content string `json:"content"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Kind = strings.TrimSpace(input.Kind)
	input.Content = strings.TrimSpace(input.Content)
	if input.Kind != "text" && input.Kind != "link" {
		writeError(w, http.StatusBadRequest, "Неизвестный тип доказательства")
		return
	}
	if input.Content == "" || len(input.Content) > 20000 {
		writeError(w, http.StatusBadRequest, "Доказательство обязательно и не длиннее 20000 символов")
		return
	}
	id, _ := newID()
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать сохранение")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `INSERT INTO task_proofs(id, record_id, author_id, kind, content, created_at) VALUES(?, ?, ?, ?, ?, ?)`, id, record.ID, user.ID, input.Kind, input.Content, nowText()); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось сохранить доказательство")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, "task", record.ID, "proof_added", "", map[string]any{"proofId": id, "kind": input.Kind}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить сохранение")
		return
	}
	proofs, _ := s.listProofs(r.Context(), record.ID)
	writeJSON(w, http.StatusCreated, proofs)
}

func (s *Server) handleCompleteTask(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if err != nil || record.Type != "task" {
		writeError(w, http.StatusNotFound, "Задача не найдена")
		return
	}
	user := currentUser(r)
	if record.OwnerID != user.ID {
		writeError(w, http.StatusForbidden, "Задачу завершает назначенный ответственный")
		return
	}
	var input struct {
		Result         string `json:"result"`
		NotifyPartners bool   `json:"notifyPartners"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	var proofCount int
	_ = s.store.db.QueryRowContext(r.Context(), `SELECT COUNT(*) FROM task_proofs WHERE record_id = ?`, record.ID).Scan(&proofCount)
	if proofCount == 0 {
		writeError(w, http.StatusConflict, "Сначала добавьте доказательство выполнения")
		return
	}
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать завершение")
		return
	}
	defer tx.Rollback()
	now := nowText()
	if _, err := tx.ExecContext(r.Context(), `UPDATE records SET status = 'completed', progress = 100, result = ?, completed_at = ?, updated_at = ? WHERE id = ?`, strings.TrimSpace(input.Result), now, now, record.ID); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить задачу")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, "task", record.ID, "completed", "", map[string]any{"proofCount": proofCount, "result": input.Result}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if input.NotifyPartners {
		if err := s.insertPartnerNotifications(r.Context(), tx, user, record, "Задача выполнена", fmt.Sprintf("%s завершил задачу «%s»", user.Username, record.Title)); err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось создать уведомление")
			return
		}
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить операцию")
		return
	}
	completed, _ := s.getRecord(r.Context(), record.ID)
	writeJSON(w, http.StatusOK, completed)
}

func (s *Server) insertPartnerNotifications(ctx context.Context, tx *sql.Tx, actor User, record Record, title, body string) error {
	rows, err := tx.QueryContext(ctx, `SELECT id FROM users WHERE id <> ?`, actor.ID)
	if err != nil {
		return err
	}
	defer rows.Close()
	ids := make([]int64, 0)
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			return err
		}
		ids = append(ids, id)
	}
	if err := rows.Close(); err != nil {
		return err
	}
	for _, id := range ids {
		notificationID, _ := newID()
		if _, err := tx.ExecContext(ctx, `INSERT INTO notifications(id, user_id, type, title, body, entity_type, entity_id, created_at) VALUES(?, ?, 'record_update', ?, ?, ?, ?, ?)`, notificationID, id, title, body, record.Type, record.ID, nowText()); err != nil {
			return err
		}
	}
	return nil
}

func (s *Server) handleNotifyPartners(w http.ResponseWriter, r *http.Request) {
	record, err := s.getRecord(r.Context(), r.PathValue("id"))
	if err != nil {
		writeError(w, http.StatusNotFound, "Карточка не найдена")
		return
	}
	user := currentUser(r)
	var input struct {
		Message string `json:"message"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	message := strings.TrimSpace(input.Message)
	if message == "" {
		message = fmt.Sprintf("%s просит посмотреть карточку «%s»", user.Username, record.Title)
	}
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать отправку")
		return
	}
	defer tx.Rollback()
	if err := s.insertPartnerNotifications(r.Context(), tx, user, record, "Обновление от партнёра", message); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось отправить уведомление")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, record.Type, record.ID, "partners_notified", "", map[string]any{"message": message}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить отправку")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"sent": true})
}

func (s *Server) handleListDefinitions(w http.ResponseWriter, r *http.Request) {
	rows, err := s.store.db.QueryContext(r.Context(), `SELECT id, key, name, scope_type, kind, active, sort_order FROM section_definitions ORDER BY active DESC, scope_type, sort_order, name`)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить структуру")
		return
	}
	defer rows.Close()
	definitions := make([]SectionDefinition, 0)
	for rows.Next() {
		var definition SectionDefinition
		var scope sql.NullString
		if err := rows.Scan(&definition.ID, &definition.Key, &definition.Name, &scope, &definition.Kind, &definition.Active, &definition.SortOrder); err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось прочитать структуру")
			return
		}
		if scope.Valid {
			definition.ScopeType = &scope.String
		}
		definitions = append(definitions, definition)
	}
	writeJSON(w, http.StatusOK, definitions)
}

func (s *Server) handleCreateDefinition(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Name      string  `json:"name"`
		ScopeType *string `json:"scopeType"`
		Kind      string  `json:"kind"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Name = strings.TrimSpace(input.Name)
	if input.Name == "" || len(input.Name) > 120 {
		writeError(w, http.StatusBadRequest, "Название раздела обязательно")
		return
	}
	if input.ScopeType != nil {
		if _, ok := recordTypes[*input.ScopeType]; !ok {
			writeError(w, http.StatusBadRequest, "Неизвестный тип карточки")
			return
		}
	}
	if input.Kind == "" {
		input.Kind = "universal"
	}
	if input.Kind != "universal" && input.Kind != "template" {
		writeError(w, http.StatusBadRequest, "Неизвестный вид раздела")
		return
	}
	id, _ := newID()
	key := "section_" + id
	user := currentUser(r)
	var sortOrder int
	_ = s.store.db.QueryRowContext(r.Context(), `SELECT COALESCE(MAX(sort_order), 0) + 10 FROM section_definitions WHERE scope_type IS ?`, input.ScopeType).Scan(&sortOrder)
	now := nowText()
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать создание")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `INSERT INTO section_definitions(id, key, name, scope_type, kind, active, sort_order, created_by, created_at, updated_at) VALUES(?, ?, ?, ?, ?, 1, ?, ?, ?, ?)`, id, key, input.Name, input.ScopeType, input.Kind, sortOrder, user.ID, now, now); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось создать раздел")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, "section_definition", id, "created", "", map[string]any{"name": input.Name, "scopeType": input.ScopeType, "kind": input.Kind}); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить создание")
		return
	}
	writeJSON(w, http.StatusCreated, map[string]any{"id": id})
}

func (s *Server) handleUpdateDefinition(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Name   *string `json:"name"`
		Active *bool   `json:"active"`
		Reason string  `json:"reason"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	updates := make([]string, 0)
	args := make([]any, 0)
	details := make(map[string]any)
	if input.Name != nil {
		value := strings.TrimSpace(*input.Name)
		if value == "" {
			writeError(w, http.StatusBadRequest, "Название не может быть пустым")
			return
		}
		updates = append(updates, "name = ?")
		args = append(args, value)
		details["name"] = value
	}
	if input.Active != nil {
		updates = append(updates, "active = ?")
		args = append(args, *input.Active)
		details["active"] = *input.Active
	}
	if len(updates) == 0 {
		writeError(w, http.StatusBadRequest, "Нет изменений")
		return
	}
	updates = append(updates, "updated_at = ?")
	args = append(args, nowText(), r.PathValue("id"))
	user := currentUser(r)
	tx, err := s.store.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось начать изменение")
		return
	}
	defer tx.Rollback()
	result, err := tx.ExecContext(r.Context(), `UPDATE section_definitions SET `+strings.Join(updates, ", ")+` WHERE id = ?`, args...)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось изменить раздел")
		return
	}
	affected, _ := result.RowsAffected()
	if affected == 0 {
		writeError(w, http.StatusNotFound, "Раздел не найден")
		return
	}
	if err := writeActivity(r.Context(), tx, user.ID, "section_definition", r.PathValue("id"), "updated", input.Reason, details); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось записать историю")
		return
	}
	if err := tx.Commit(); err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось завершить изменение")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"updated": true})
}

func (s *Server) handleNotifications(w http.ResponseWriter, r *http.Request) {
	user := currentUser(r)
	rows, err := s.store.db.QueryContext(r.Context(), `SELECT id, type, title, body, entity_type, entity_id, read_at, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 200`, user.ID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить уведомления")
		return
	}
	defer rows.Close()
	notifications := make([]Notification, 0)
	for rows.Next() {
		var n Notification
		var entityType, entityID, readAt sql.NullString
		if err := rows.Scan(&n.ID, &n.Type, &n.Title, &n.Body, &entityType, &entityID, &readAt, &n.CreatedAt); err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось прочитать уведомления")
			return
		}
		if entityType.Valid {
			n.EntityType = &entityType.String
		}
		if entityID.Valid {
			n.EntityID = &entityID.String
		}
		if readAt.Valid {
			n.ReadAt = &readAt.String
		}
		notifications = append(notifications, n)
	}
	writeJSON(w, http.StatusOK, notifications)
}

func (s *Server) handleReadNotification(w http.ResponseWriter, r *http.Request) {
	user := currentUser(r)
	_, _ = s.store.db.ExecContext(r.Context(), `UPDATE notifications SET read_at = COALESCE(read_at, ?) WHERE id = ? AND user_id = ?`, nowText(), r.PathValue("id"), user.ID)
	w.WriteHeader(http.StatusNoContent)
}
func (s *Server) handleReadAllNotifications(w http.ResponseWriter, r *http.Request) {
	user := currentUser(r)
	_, _ = s.store.db.ExecContext(r.Context(), `UPDATE notifications SET read_at = COALESCE(read_at, ?) WHERE user_id = ?`, nowText(), user.ID)
	w.WriteHeader(http.StatusNoContent)
}

func (s *Server) handleActivity(w http.ResponseWriter, r *http.Request) {
	where := []string{"1 = 1"}
	args := make([]any, 0)
	if entityType := strings.TrimSpace(r.URL.Query().Get("entityType")); entityType != "" {
		where = append(where, "a.entity_type = ?")
		args = append(args, entityType)
	}
	if entityID := strings.TrimSpace(r.URL.Query().Get("entityId")); entityID != "" {
		where = append(where, "a.entity_id = ?")
		args = append(args, entityID)
	}
	rows, err := s.store.db.QueryContext(r.Context(), `SELECT a.id, a.actor_id, u.username, a.entity_type, a.entity_id, a.action, a.details_json, a.reason, a.created_at FROM activity a JOIN users u ON u.id = a.actor_id WHERE `+strings.Join(where, " AND ")+` ORDER BY a.created_at DESC LIMIT 500`, args...)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить историю")
		return
	}
	defer rows.Close()
	activity := make([]Activity, 0)
	for rows.Next() {
		var item Activity
		var details string
		if err := rows.Scan(&item.ID, &item.ActorID, &item.ActorUsername, &item.EntityType, &item.EntityID, &item.Action, &details, &item.Reason, &item.CreatedAt); err != nil {
			writeError(w, http.StatusInternalServerError, "Не удалось прочитать историю")
			return
		}
		if err := json.Unmarshal([]byte(details), &item.Details); err != nil {
			item.Details = map[string]any{"raw": details}
		}
		activity = append(activity, item)
	}
	writeJSON(w, http.StatusOK, activity)
}

func decodeJSON(w http.ResponseWriter, r *http.Request, target any) bool {
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		if errors.Is(err, io.EOF) {
			writeError(w, http.StatusBadRequest, "Пустой запрос")
		} else {
			writeError(w, http.StatusBadRequest, "Некорректные данные запроса")
		}
		return false
	}
	return true
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	if status != http.StatusNoContent {
		_ = json.NewEncoder(w).Encode(value)
	}
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
