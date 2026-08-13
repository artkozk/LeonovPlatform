package app

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/cookiejar"
	"net/http/httptest"
	"path/filepath"
	"testing"
)

func TestBusinessWorkflow(t *testing.T) {
	store, err := OpenStore(filepath.Join(t.TempDir(), "workflow.db"))
	if err != nil {
		t.Fatalf("open store: %v", err)
	}
	defer store.Close()

	server := httptest.NewServer(NewServer(store, Config{SessionLifetime: 24 * 60 * 60 * 1e9}))
	defer server.Close()
	artkozk := testClient(t)
	sweetybboy := testClient(t)

	register(t, artkozk, server.URL, "artkozk@example.test", "artkozk")
	partner := register(t, sweetybboy, server.URL, "sweetybboy@example.test", "sweetybboy")

	var me User
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/me", nil, http.StatusOK, &me)
	if me.Username != "artkozk" {
		t.Fatalf("persistent session returned username %q", me.Username)
	}

	criterion := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "criterion", "title": "Проверяемость спроса", "description": "Можно проверить за неделю",
	})
	idea := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "idea", "title": "Кормить голубей", "description": "Сырая идея без предварительной оценки",
	})
	if idea.Status != "inbox" {
		t.Fatalf("new idea status = %q, want inbox", idea.Status)
	}

	var moved Record
	requestJSON(t, artkozk, http.MethodPatch, server.URL+"/api/records/"+idea.ID, map[string]any{
		"status": "review", "reason": "Нужно проверить спрос",
	}, http.StatusOK, &moved)
	if moved.ID != idea.ID || moved.Status != "review" {
		t.Fatalf("idea transition copied or lost record: before=%s after=%s status=%s", idea.ID, moved.ID, moved.Status)
	}

	var reviewIdeas []Record
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records?type=idea&status=review", nil, http.StatusOK, &reviewIdeas)
	if len(reviewIdeas) != 1 || reviewIdeas[0].ID != idea.ID {
		t.Fatalf("derived review view = %#v", reviewIdeas)
	}

	var sections []RecordSection
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+idea.ID+"/sections", map[string]any{
		"definitionId": "default-limitations", "title": "Ограничения", "content": "Нельзя вредить городской среде",
	}, http.StatusOK, &sections)
	if len(sections) < 9 {
		t.Fatalf("idea universal sections = %d, want at least 9", len(sections))
	}

	var scores []CriterionScore
	requestJSON(t, artkozk, http.MethodPut, server.URL+"/api/records/"+idea.ID+"/criteria/"+criterion.ID, map[string]any{
		"score": 7, "note": "Есть быстрый полевой тест", "reason": "Первая оценка",
	}, http.StatusOK, &scores)
	if len(scores) != 1 || scores[0].Score != 7 {
		t.Fatalf("criterion scores = %#v", scores)
	}

	var links []RecordLink
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+idea.ID+"/links", map[string]any{
		"targetId": criterion.ID, "relationType": "evaluated_by",
	}, http.StatusCreated, &links)
	if len(links) != 1 || links[0].Record.ID != criterion.ID {
		t.Fatalf("record links = %#v", links)
	}

	task := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "task", "title": "Расписать вопросы до совместной работы", "ownerId": partner.ID,
		"estimateMinutes": 90, "dueAt": "2026-08-12T12:00:00Z",
	})

	var taskEdited Record
	requestJSON(t, artkozk, http.MethodPatch, server.URL+"/api/records/"+task.ID, map[string]any{
		"title": "Расписать вопросы к совместной работе", "dueAt": "2026-08-12T12:00:00.000Z",
		"expectedUpdatedAt": task.UpdatedAt,
	}, http.StatusOK, &taskEdited)
	if taskEdited.Title != "Расписать вопросы к совместной работе" || taskEdited.DueAt == nil || *taskEdited.DueAt != "2026-08-12T12:00:00Z" {
		t.Fatalf("same deadline update changed deadline or failed without reason: %#v", taskEdited)
	}

	requestJSON(t, artkozk, http.MethodPatch, server.URL+"/api/records/"+task.ID, map[string]any{
		"dueAt": "2026-08-13T12:00:00Z", "expectedUpdatedAt": taskEdited.UpdatedAt,
	}, http.StatusBadRequest, nil)

	requestJSON(t, artkozk, http.MethodPatch, server.URL+"/api/records/"+task.ID, map[string]any{
		"description": "Конфликтующая старая версия", "expectedUpdatedAt": task.UpdatedAt,
	}, http.StatusConflict, nil)
	task = taskEdited

	requestJSON(t, sweetybboy, http.MethodPost, server.URL+"/api/records/"+task.ID+"/complete", map[string]any{
		"result": "Вопросы готовы", "notifyPartners": true,
	}, http.StatusConflict, nil)

	var proofs []Proof
	requestJSON(t, sweetybboy, http.MethodPost, server.URL+"/api/records/"+task.ID+"/proofs", map[string]any{
		"kind": "text", "content": "1. Какие роли у каждого?\n2. Как принимаем спорные решения?",
	}, http.StatusCreated, &proofs)
	if len(proofs) != 1 {
		t.Fatalf("proof count = %d", len(proofs))
	}

	var completed Record
	requestJSON(t, sweetybboy, http.MethodPost, server.URL+"/api/records/"+task.ID+"/complete", map[string]any{
		"result": "Подготовлены вопросы для установочной встречи", "notifyPartners": true,
	}, http.StatusOK, &completed)
	if completed.Status != "completed" || completed.Progress != 100 || completed.ProofCount != 1 {
		t.Fatalf("completed task = %#v", completed)
	}

	var notifications []Notification
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/notifications", nil, http.StatusOK, &notifications)
	if len(notifications) != 1 || notifications[0].EntityID == nil || *notifications[0].EntityID != task.ID {
		t.Fatalf("completion notifications = %#v", notifications)
	}

	var activity []Activity
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/activity?entityId="+idea.ID, nil, http.StatusOK, &activity)
	if len(activity) < 5 {
		t.Fatalf("idea activity entries = %d, want at least 5", len(activity))
	}
	foundStatusTransition := false
	for _, item := range activity {
		if item.Action != "updated" {
			continue
		}
		statusChange, ok := item.Details["status"].(map[string]any)
		if ok && statusChange["before"] == "inbox" && statusChange["after"] == "review" && item.Reason == "Нужно проверить спрос" {
			foundStatusTransition = true
		}
	}
	if !foundStatusTransition {
		t.Fatalf("activity does not preserve status before/after and reason: %#v", activity)
	}

	var renamed User
	requestJSON(t, artkozk, http.MethodPatch, server.URL+"/api/me", map[string]any{
		"username": "artkozk_new",
	}, http.StatusOK, &renamed)
	if renamed.Username != "artkozk_new" {
		t.Fatalf("updated username = %q", renamed.Username)
	}
}

func testClient(t *testing.T) *http.Client {
	t.Helper()
	jar, err := cookiejar.New(nil)
	if err != nil {
		t.Fatalf("create cookie jar: %v", err)
	}
	return &http.Client{Jar: jar}
}

func register(t *testing.T, client *http.Client, baseURL, email, username string) User {
	t.Helper()
	var user User
	requestJSON(t, client, http.MethodPost, baseURL+"/api/auth/register", map[string]any{
		"email": email, "username": username, "password": "strong-password-123",
	}, http.StatusCreated, &user)
	return user
}

func createRecord(t *testing.T, client *http.Client, baseURL string, body map[string]any) Record {
	t.Helper()
	var record Record
	requestJSON(t, client, http.MethodPost, baseURL+"/api/records", body, http.StatusCreated, &record)
	return record
}

func requestJSON(t *testing.T, client *http.Client, method, url string, body any, wantStatus int, target any) {
	t.Helper()
	var reader io.Reader
	if body != nil {
		payload, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal request: %v", err)
		}
		reader = bytes.NewReader(payload)
	}
	request, err := http.NewRequest(method, url, reader)
	if err != nil {
		t.Fatalf("create request: %v", err)
	}
	if body != nil {
		request.Header.Set("Content-Type", "application/json")
	}
	response, err := client.Do(request)
	if err != nil {
		t.Fatalf("request %s %s: %v", method, url, err)
	}
	defer response.Body.Close()
	responseBody, _ := io.ReadAll(response.Body)
	if response.StatusCode != wantStatus {
		t.Fatalf("%s %s status=%d want=%d body=%s", method, url, response.StatusCode, wantStatus, responseBody)
	}
	if target != nil && len(responseBody) > 0 {
		if err := json.Unmarshal(responseBody, target); err != nil {
			t.Fatalf("decode response %s: %v; body=%s", url, err, responseBody)
		}
	}
}
