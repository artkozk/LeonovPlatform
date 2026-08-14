package app

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"
)

type UserActivityDay struct {
	Date          string `json:"date"`
	ActiveSeconds int    `json:"activeSeconds"`
	Interactions  int    `json:"interactions"`
	LastSeenAt    string `json:"lastSeenAt"`
}

type UserProfile struct {
	User                User              `json:"user"`
	ActiveSeconds30Days int               `json:"activeSeconds30Days"`
	Interactions30Days  int               `json:"interactions30Days"`
	Actions30Days       int               `json:"actions30Days"`
	CompletedRecords    int               `json:"completedRecords"`
	EstimateMinutes     int               `json:"estimateMinutes"`
	ActualMinutes       int               `json:"actualMinutes"`
	Activity            []UserActivityDay `json:"activity"`
	RecentActions       []Activity        `json:"recentActions"`
}

func (s *Server) handlePresence(w http.ResponseWriter, r *http.Request) {
	var input struct {
		ActiveSeconds int `json:"activeSeconds"`
		Interactions  int `json:"interactions"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	if input.ActiveSeconds < 0 {
		input.ActiveSeconds = 0
	}
	if input.ActiveSeconds > 120 {
		input.ActiveSeconds = 120
	}
	if input.Interactions < 0 {
		input.Interactions = 0
	}
	if input.Interactions > 500 {
		input.Interactions = 500
	}
	user := currentUser(r)
	now := time.Now().UTC()
	date := now.Format("2006-01-02")
	_, err := s.store.db.ExecContext(r.Context(), `
		INSERT INTO user_activity_daily(user_id, activity_date, active_seconds, interactions, last_seen_at)
		VALUES(?, ?, ?, ?, ?)
		ON CONFLICT(user_id, activity_date) DO UPDATE SET
			active_seconds = active_seconds + excluded.active_seconds,
			interactions = interactions + excluded.interactions,
			last_seen_at = excluded.last_seen_at`, user.ID, date, input.ActiveSeconds, input.Interactions, nowText())
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось сохранить активность")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (s *Server) handleUserProfile(w http.ResponseWriter, r *http.Request) {
	userID, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil {
		writeError(w, http.StatusBadRequest, "Некорректный участник")
		return
	}
	var profile UserProfile
	err = s.store.db.QueryRowContext(r.Context(), `SELECT id, email, username, created_at FROM users WHERE id = ?`, userID).
		Scan(&profile.User.ID, &profile.User.Email, &profile.User.Username, &profile.User.CreatedAt)
	if errors.Is(err, sql.ErrNoRows) {
		writeError(w, http.StatusNotFound, "Участник не найден")
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Не удалось загрузить профиль")
		return
	}
	since := time.Now().UTC().AddDate(0, 0, -29).Format("2006-01-02")
	_ = s.store.db.QueryRowContext(r.Context(), `SELECT COALESCE(SUM(active_seconds), 0), COALESCE(SUM(interactions), 0) FROM user_activity_daily WHERE user_id = ? AND activity_date >= ?`, userID, since).
		Scan(&profile.ActiveSeconds30Days, &profile.Interactions30Days)
	_ = s.store.db.QueryRowContext(r.Context(), `SELECT COUNT(*) FROM activity WHERE actor_id = ? AND created_at >= ?`, userID, time.Now().UTC().AddDate(0, 0, -30).Format(time.RFC3339Nano)).Scan(&profile.Actions30Days)
	_ = s.store.db.QueryRowContext(r.Context(), `SELECT COUNT(*), COALESCE(SUM(estimate_minutes), 0), COALESCE(SUM(actual_minutes), 0) FROM records WHERE owner_id = ? AND status = 'completed'`, userID).
		Scan(&profile.CompletedRecords, &profile.EstimateMinutes, &profile.ActualMinutes)

	profile.Activity = make([]UserActivityDay, 0)
	rows, err := s.store.db.QueryContext(r.Context(), `SELECT activity_date, active_seconds, interactions, last_seen_at FROM user_activity_daily WHERE user_id = ? ORDER BY activity_date DESC LIMIT 30`, userID)
	if err == nil {
		for rows.Next() {
			var day UserActivityDay
			if rows.Scan(&day.Date, &day.ActiveSeconds, &day.Interactions, &day.LastSeenAt) == nil {
				profile.Activity = append(profile.Activity, day)
			}
		}
		rows.Close()
	}
	profile.RecentActions, _ = s.listUserActivity(r.Context(), userID, 40)
	writeJSON(w, http.StatusOK, profile)
}

func (s *Server) listUserActivity(ctx context.Context, userID int64, limit int) ([]Activity, error) {
	rows, err := s.store.db.QueryContext(ctx, `SELECT a.id, a.actor_id, u.username, a.entity_type, a.entity_id, a.action, a.details_json, a.reason, a.created_at FROM activity a JOIN users u ON u.id = a.actor_id WHERE a.actor_id = ? ORDER BY a.created_at DESC LIMIT ?`, userID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	items := make([]Activity, 0)
	for rows.Next() {
		var item Activity
		var details string
		if err := rows.Scan(&item.ID, &item.ActorID, &item.ActorUsername, &item.EntityType, &item.EntityID, &item.Action, &details, &item.Reason, &item.CreatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(details), &item.Details)
		items = append(items, item)
	}
	return items, rows.Err()
}

type RecordSuggestion struct {
	Priority   string `json:"priority"`
	Workstream string `json:"workstream"`
	ParentID   string `json:"parentId"`
	Reason     string `json:"reason"`
	Source     string `json:"source"`
}

func (s *Server) handleSuggestRecord(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Type        string `json:"type"`
		Title       string `json:"title"`
		Description string `json:"description"`
	}
	if !decodeJSON(w, r, &input) {
		return
	}
	input.Title = strings.TrimSpace(input.Title)
	input.Description = strings.TrimSpace(input.Description)
	if input.Title == "" {
		writeError(w, http.StatusBadRequest, "Сначала укажите название")
		return
	}
	suggestion := s.heuristicSuggestion(r.Context(), input.Type, input.Title, input.Description)
	if s.config.GroqAPIKey != "" {
		if aiSuggestion, err := s.groqSuggestion(r.Context(), input.Type, input.Title, input.Description); err == nil {
			suggestion = aiSuggestion
		}
	}
	writeJSON(w, http.StatusOK, suggestion)
}

func (s *Server) heuristicSuggestion(ctx context.Context, recordType, title, description string) RecordSuggestion {
	text := strings.ToLower(title + " " + description)
	priority := "normal"
	if strings.Contains(text, "сроч") || strings.Contains(text, "критич") || strings.Contains(text, "блокир") {
		priority = "critical"
	} else if strings.Contains(text, "важн") || strings.Contains(text, "релиз") || strings.Contains(text, "дедлайн") {
		priority = "high"
	}
	workstream := "business"
	if strings.Contains(text, "платформ") || strings.Contains(text, "интерфейс") || strings.Contains(text, "api") || strings.Contains(text, "баг") || strings.Contains(text, "сервер") || strings.Contains(text, "дизайн") {
		workstream = "platform"
	}
	parentID := ""
	var candidate string
	_ = s.store.db.QueryRowContext(ctx, `SELECT id FROM records WHERE status NOT IN ('archived', 'cancelled', 'completed') AND is_root = 1 AND workstream = ? ORDER BY updated_at DESC LIMIT 1`, workstream).Scan(&candidate)
	if candidate != "" {
		parentID = candidate
	}
	return RecordSuggestion{Priority: priority, Workstream: workstream, ParentID: parentID, Reason: "Предложено по формулировке и текущим корневым карточкам. Проверьте перед сохранением.", Source: "heuristic"}
}

func (s *Server) groqSuggestion(ctx context.Context, recordType, title, description string) (RecordSuggestion, error) {
	ctx, cancel := context.WithTimeout(ctx, 12*time.Second)
	defer cancel()
	parentRows, err := s.store.db.QueryContext(ctx, `SELECT id, title, type, workstream FROM records WHERE status NOT IN ('archived', 'cancelled') AND (is_root = 1 OR parent_id IS NULL) ORDER BY updated_at DESC LIMIT 40`)
	if err != nil {
		return RecordSuggestion{}, err
	}
	parents := make([]map[string]string, 0)
	for parentRows.Next() {
		var id, parentTitle, parentType, workstream string
		if parentRows.Scan(&id, &parentTitle, &parentType, &workstream) == nil {
			parents = append(parents, map[string]string{"id": id, "title": parentTitle, "type": parentType, "workstream": workstream})
		}
	}
	parentRows.Close()
	parentJSON, _ := json.Marshal(parents)
	prompt := fmt.Sprintf("Определи priority (low|normal|high|critical), workstream (business|platform|operations) и parentId из списка или пустую строку. Верни только JSON {priority,workstream,parentId,reason}. Тип: %s. Название: %s. Описание: %s. Возможные родители: %s", recordType, title, description, parentJSON)
	payload := map[string]any{
		"model":                 s.config.GroqModel,
		"messages":              []map[string]string{{"role": "system", "content": "Ты помощник закрытой системы двух сооснователей. Не выдумывай идентификаторы. Ответ только валидным JSON."}, {"role": "user", "content": prompt}},
		"temperature":           0.1,
		"max_completion_tokens": 450,
		"response_format":       map[string]string{"type": "json_object"},
	}
	body, _ := json.Marshal(payload)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, "https://api.groq.com/openai/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return RecordSuggestion{}, err
	}
	req.Header.Set("Authorization", "Bearer "+s.config.GroqAPIKey)
	req.Header.Set("Content-Type", "application/json")
	response, err := http.DefaultClient.Do(req)
	if err != nil {
		return RecordSuggestion{}, err
	}
	defer response.Body.Close()
	responseBody, _ := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	if response.StatusCode != http.StatusOK {
		return RecordSuggestion{}, fmt.Errorf("groq status %d", response.StatusCode)
	}
	var completion struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}
	if err := json.Unmarshal(responseBody, &completion); err != nil || len(completion.Choices) == 0 {
		return RecordSuggestion{}, errors.New("invalid groq response")
	}
	var suggestion RecordSuggestion
	if err := json.Unmarshal([]byte(completion.Choices[0].Message.Content), &suggestion); err != nil {
		return RecordSuggestion{}, err
	}
	if !validPriority(suggestion.Priority) || !validWorkstream(suggestion.Workstream) {
		return RecordSuggestion{}, errors.New("invalid groq suggestion")
	}
	if suggestion.ParentID != "" {
		if _, err := s.getRecord(ctx, suggestion.ParentID); err != nil {
			suggestion.ParentID = ""
		}
	}
	suggestion.Source = "groq"
	return suggestion, nil
}
