package app

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/cookiejar"
	"net/http/httptest"
	"path/filepath"
	"strconv"
	"strings"
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
	var ideaDetail struct {
		Links           []RecordLink     `json:"links"`
		Scores          []CriterionScore `json:"scores"`
		RelationsLoaded bool             `json:"relationsLoaded"`
	}
	detailHeaders := requestGetJSONWithHeaders(t, artkozk, server.URL+"/api/records/"+idea.ID, &ideaDetail)
	if ideaDetail.RelationsLoaded || len(ideaDetail.Links) != 0 || len(ideaDetail.Scores) != 0 {
		t.Fatalf("initial detail must defer relations: %#v", ideaDetail)
	}
	if !strings.Contains(detailHeaders.Get("Server-Timing"), "record-detail") {
		t.Fatalf("detail Server-Timing = %q", detailHeaders.Get("Server-Timing"))
	}
	var ideaRelations struct {
		Links  []RecordLink     `json:"links"`
		Scores []CriterionScore `json:"scores"`
	}
	relationHeaders := requestGetJSONWithHeaders(t, artkozk, server.URL+"/api/records/"+idea.ID+"/relations", &ideaRelations)
	if len(ideaRelations.Links) != 1 || len(ideaRelations.Scores) != 1 {
		t.Fatalf("lazy relations = %#v", ideaRelations)
	}
	if !strings.Contains(relationHeaders.Get("Server-Timing"), "record-relations") {
		t.Fatalf("relations Server-Timing = %q", relationHeaders.Get("Server-Timing"))
	}

	task := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "task", "title": "Расписать вопросы до совместной работы", "ownerId": partner.ID,
		"estimateMinutes": 90, "dueAt": "2026-08-12T12:00:00Z",
	})
	convertibleTask := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "task", "title": "Список вопросов основателей", "ownerId": me.ID,
		"estimateMinutes": 120, "dueAt": "2026-08-20T12:00:00Z",
	})
	var convertedQuestionSet Record
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+convertibleTask.ID+"/convert-to-questions", map[string]any{
		"reason": "Задача на самом деле является совместной проработкой вопросов", "expectedUpdatedAt": convertibleTask.UpdatedAt,
	}, http.StatusOK, &convertedQuestionSet)
	if convertedQuestionSet.ID != convertibleTask.ID || convertedQuestionSet.Type != "question_set" || convertedQuestionSet.Status != "planned" || convertedQuestionSet.EstimateMinutes != 120 || convertedQuestionSet.DueAt == nil || *convertedQuestionSet.DueAt != "2026-08-20T12:00:00Z" {
		t.Fatalf("converted task must preserve identity and planning fields: before=%#v after=%#v", convertibleTask, convertedQuestionSet)
	}

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
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+task.ID+"/convert-to-questions", map[string]any{
		"reason": "Проверка защиты данных",
	}, http.StatusConflict, nil)

	var notifications []Notification
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/notifications", nil, http.StatusOK, &notifications)
	if len(notifications) != 1 || notifications[0].EntityID == nil || *notifications[0].EntityID != task.ID {
		t.Fatalf("completion notifications = %#v", notifications)
	}

	questionSet := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "question_set", "title": "Вопросы до начала совместной работы", "ownerId": me.ID,
	})
	if questionSet.Type != "question_set" || questionSet.Status != "planned" {
		t.Fatalf("question set = %#v", questionSet)
	}
	var workflow QuestionWorkflow
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions", map[string]any{
		"questions": "1. Как распределяем роли?\n2. Как принимаем спорные решения?",
	}, http.StatusCreated, &workflow)
	if len(workflow.Questions) != 2 || workflow.Expected != 4 || workflow.Answered != 0 {
		t.Fatalf("question workflow after create = %#v", workflow)
	}
	var artPending, partnerPending []PendingQuestion
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/questions/pending", nil, http.StatusOK, &artPending)
	requestJSON(t, sweetybboy, http.MethodGet, server.URL+"/api/questions/pending", nil, http.StatusOK, &partnerPending)
	if len(artPending) != 2 || len(partnerPending) != 2 || artPending[0].RecordID != questionSet.ID {
		t.Fatalf("pending questions before answers: art=%#v partner=%#v", artPending, partnerPending)
	}
	var activeQuestionSet Record
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+questionSet.ID, nil, http.StatusOK, &struct {
		Record *Record `json:"record"`
	}{Record: &activeQuestionSet})
	if activeQuestionSet.Status != "in_progress" {
		t.Fatalf("question set with open questions status = %q, want in_progress", activeQuestionSet.Status)
	}
	firstQuestion := workflow.Questions[0]
	requestJSON(t, artkozk, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+firstQuestion.ID+"/answer", map[string]any{
		"content": "Я веду продукт и продажи.",
	}, http.StatusOK, &workflow)
	if workflow.Answered != 1 || len(workflow.Questions[0].Answers) != 1 {
		t.Fatalf("first founder answer = %#v", workflow)
	}
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/questions/pending", nil, http.StatusOK, &artPending)
	requestJSON(t, sweetybboy, http.MethodGet, server.URL+"/api/questions/pending", nil, http.StatusOK, &partnerPending)
	if len(artPending) != 1 || len(partnerPending) != 2 {
		t.Fatalf("pending questions must be personal: art=%#v partner=%#v", artPending, partnerPending)
	}
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+firstQuestion.ID+"/decision", map[string]any{
		"mode": "answer", "answerId": workflow.Questions[0].Answers[0].ID,
	}, http.StatusConflict, nil)
	requestJSON(t, sweetybboy, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+firstQuestion.ID+"/answer", map[string]any{
		"content": "Я веду операции и финансы.",
	}, http.StatusOK, &workflow)
	if workflow.Answered != 2 || len(workflow.Questions[0].Answers) != 2 {
		t.Fatalf("separate founder answers = %#v", workflow)
	}
	var artAnswerID string
	for _, answer := range workflow.Questions[0].Answers {
		if answer.AuthorUsername == "artkozk" {
			artAnswerID = answer.ID
		}
	}
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+firstQuestion.ID+"/decision", map[string]any{
		"mode": "answer", "answerId": artAnswerID,
	}, http.StatusOK, &workflow)
	if workflow.Resolved != 1 || workflow.Questions[0].Decision == nil || workflow.Questions[0].Decision.SourceAnswerID == nil || *workflow.Questions[0].Decision.SourceAnswerID != artAnswerID {
		t.Fatalf("decision selected from answer = %#v", workflow)
	}
	secondQuestion := workflow.Questions[1]
	for clientIndex, client := range []*http.Client{artkozk, sweetybboy} {
		requestJSON(t, client, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+secondQuestion.ID+"/answer", map[string]any{
			"content": []string{"Решает владелец области.", "Решаем консенсусом."}[clientIndex],
		}, http.StatusOK, &workflow)
	}
	requestJSON(t, sweetybboy, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+secondQuestion.ID+"/decision", map[string]any{
		"mode": "custom", "content": "Сначала ищем консенсус, при тупике решает владелец области.",
	}, http.StatusOK, &workflow)
	if workflow.Resolved != 2 || workflow.Questions[1].Decision == nil || workflow.Questions[1].Decision.SourceAnswerID != nil {
		t.Fatalf("custom joint decision = %#v", workflow)
	}
	var rule Record
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+secondQuestion.ID+"/outputs", map[string]any{
		"kind": "rule", "title": "Контрольные решения принимает владелец области", "ownerId": me.ID,
	}, http.StatusCreated, &rule)
	if rule.Type != "decision" || rule.Kind != "rule" || rule.Description != workflow.Questions[1].Decision.Content {
		t.Fatalf("rule created from question decision = %#v", rule)
	}
	var ruleDetail struct {
		Record     Record            `json:"record"`
		Derivation *RecordDerivation `json:"derivation"`
	}
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+rule.ID, nil, http.StatusOK, &ruleDetail)
	if ruleDetail.Derivation == nil || ruleDetail.Derivation.SourceRecordID != questionSet.ID || ruleDetail.Derivation.SourceQuestionID != secondQuestion.ID || ruleDetail.Derivation.DecisionContent != workflow.Questions[1].Decision.Content {
		t.Fatalf("rule derivation must preserve exact source chain: %#v", ruleDetail)
	}
	originalDecision := ruleDetail.Derivation.DecisionContent
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+secondQuestion.ID+"/decision", map[string]any{
		"mode": "custom", "content": "После пересмотра контрольное решение принимаем только вместе.",
	}, http.StatusOK, &workflow)
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+rule.ID, nil, http.StatusOK, &ruleDetail)
	if ruleDetail.Derivation == nil || ruleDetail.Derivation.DecisionContent != originalDecision {
		t.Fatalf("rule derivation changed after source decision edit: %#v", ruleDetail.Derivation)
	}
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+questionSet.ID, nil, http.StatusOK, &struct {
		QuestionWorkflow *QuestionWorkflow `json:"questionWorkflow"`
	}{QuestionWorkflow: &workflow})
	if len(workflow.Questions[1].Outputs) != 1 || workflow.Questions[1].Outputs[0].RecordID != rule.ID {
		t.Fatalf("question output missing from workflow: %#v", workflow.Questions[1].Outputs)
	}
	meeting := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "meeting", "title": "Установочная встреча", "description": "Сузили круг направлений", "ownerId": me.ID, "dueAt": "2026-08-14T16:00:00Z",
	})
	if meeting.Type != "meeting" || meeting.Kind != "meeting" || meeting.Status != "planned" {
		t.Fatalf("meeting card = %#v", meeting)
	}
	decisionTask := createRecord(t, artkozk, server.URL, map[string]any{
		"type": "task", "title": "Реализовать совместное решение", "ownerId": me.ID,
	})
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/links", map[string]any{
		"targetId": decisionTask.ID, "relationType": "leads_to", "reason": "Задача создана из совместного решения",
	}, http.StatusCreated, &links)
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+questionSet.ID+"/relations", nil, http.StatusOK, &ideaRelations)
	linkedDecisionTask := false
	for _, link := range ideaRelations.Links {
		if link.Record.ID == decisionTask.ID && link.RelationType == "leads_to" {
			linkedDecisionTask = true
		}
	}
	if !linkedDecisionTask {
		t.Fatalf("question decision task link missing: %#v", ideaRelations.Links)
	}
	var completedQuestionSet Record
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+questionSet.ID, nil, http.StatusOK, &struct {
		Record *Record `json:"record"`
	}{Record: &completedQuestionSet})
	if completedQuestionSet.Status != "completed" {
		t.Fatalf("question set must complete automatically = %#v", completedQuestionSet)
	}
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions", map[string]any{
		"questions": "Новый вопрос после завершения",
	}, http.StatusCreated, &workflow)
	requestJSON(t, artkozk, http.MethodGet, server.URL+"/api/records/"+questionSet.ID, nil, http.StatusOK, &struct {
		Record *Record `json:"record"`
	}{Record: &activeQuestionSet})
	if activeQuestionSet.Status != "in_progress" || activeQuestionSet.Progress >= 100 {
		t.Fatalf("new question must reopen workflow = %#v", activeQuestionSet)
	}
	newQuestion := workflow.Questions[len(workflow.Questions)-1]
	requestJSON(t, artkozk, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+newQuestion.ID+"/archive", map[string]any{
		"reason": "Вопрос добавлен по ошибке",
	}, http.StatusOK, &workflow)

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

func TestQuestionDecisionWaitsForSecondFounder(t *testing.T) {
	store, err := OpenStore(filepath.Join(t.TempDir(), "single-founder.db"))
	if err != nil {
		t.Fatalf("open store: %v", err)
	}
	defer store.Close()
	server := httptest.NewServer(NewServer(store, Config{SessionLifetime: 24 * 60 * 60 * 1e9}))
	defer server.Close()
	client := testClient(t)
	founder := register(t, client, server.URL, "founder@example.test", "founder")
	questionSet := createRecord(t, client, server.URL, map[string]any{
		"type": "question_set", "title": "Договорённости", "ownerId": founder.ID,
	})
	var workflow QuestionWorkflow
	requestJSON(t, client, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions", map[string]any{
		"questions": "Кто принимает финальное решение?",
	}, http.StatusCreated, &workflow)
	if workflow.UserCount != 2 || workflow.Expected != 2 {
		t.Fatalf("single registered founder must still require two answers: %#v", workflow)
	}
	question := workflow.Questions[0]
	requestJSON(t, client, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+question.ID+"/answer", map[string]any{
		"content": "Решает владелец области.",
	}, http.StatusOK, &workflow)
	answerID := workflow.Questions[0].Answers[0].ID
	requestJSON(t, client, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+question.ID+"/decision", map[string]any{
		"mode": "answer", "answerId": answerID,
	}, http.StatusConflict, nil)
}

func TestGraphSearchAndPriority(t *testing.T) {
	store, err := OpenStore(filepath.Join(t.TempDir(), "graph.db"))
	if err != nil {
		t.Fatalf("open store: %v", err)
	}
	defer store.Close()

	server := httptest.NewServer(NewServer(store, Config{SessionLifetime: 24 * 60 * 60 * 1e9}))
	defer server.Close()
	client := testClient(t)
	partnerClient := testClient(t)
	user := register(t, client, server.URL, "founder@example.test", "founder")
	register(t, partnerClient, server.URL, "partner@example.test", "partner")

	questionSet := createRecord(t, client, server.URL, map[string]any{
		"type": "question_set", "title": "Вопросы о ролях", "ownerId": user.ID,
		"priority": "critical", "dueAt": "2026-08-18T12:00:00Z", "estimateMinutes": 120,
	})
	if questionSet.Priority != "critical" {
		t.Fatalf("created priority = %q, want critical", questionSet.Priority)
	}

	var workflow QuestionWorkflow
	requestJSON(t, client, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions", map[string]any{
		"questions": "Кто принимает контрольное решение?",
	}, http.StatusCreated, &workflow)
	if len(workflow.Questions) != 1 {
		t.Fatalf("questions = %#v", workflow.Questions)
	}
	question := workflow.Questions[0]
	requestJSON(t, client, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+question.ID+"/answer", map[string]any{
		"content": "Контрольное решение принимает владелец направления.",
	}, http.StatusOK, &workflow)
	requestJSON(t, partnerClient, http.MethodPut, server.URL+"/api/records/"+questionSet.ID+"/questions/"+question.ID+"/answer", map[string]any{
		"content": "Согласен, если владелец направления заранее назначен.",
	}, http.StatusOK, &workflow)
	requestJSON(t, client, http.MethodPost, server.URL+"/api/records/"+questionSet.ID+"/questions/"+question.ID+"/decision", map[string]any{
		"mode": "answer", "answerId": workflow.Questions[0].Answers[0].ID,
	}, http.StatusOK, &workflow)

	var graph GraphResponse
	graphHeaders := requestGetJSONWithHeaders(t, client, server.URL+"/api/graph", &graph)
	if !strings.Contains(graphHeaders.Get("Server-Timing"), "graph") {
		t.Fatalf("graph Server-Timing = %q", graphHeaders.Get("Server-Timing"))
	}
	wantNodeKinds := map[string]bool{"record": false, "question": false, "answer": false, "joint_decision": false}
	for _, node := range graph.Nodes {
		if _, ok := wantNodeKinds[node.EntityKind]; ok {
			wantNodeKinds[node.EntityKind] = true
		}
	}
	for kind, found := range wantNodeKinds {
		if !found {
			t.Fatalf("graph missing %s node: %#v", kind, graph.Nodes)
		}
	}
	if len(graph.Edges) < 3 {
		t.Fatalf("graph edges = %d, want question workflow chain", len(graph.Edges))
	}

	var search []SearchResult
	requestJSON(t, client, http.MethodGet, server.URL+"/api/search?q="+"%D0%BA%D0%BE%D0%BD%D1%82%D1%80%D0%BE%D0%BB%D1%8C%D0%BD%D0%BE%D0%B5", nil, http.StatusOK, &search)
	if len(search) < 2 {
		t.Fatalf("global search must find question, answer and/or decision: %#v", search)
	}
	foundQuestion := false
	for _, result := range search {
		if result.EntityKind == "question" && result.RecordID == questionSet.ID {
			foundQuestion = true
		}
	}
	if !foundQuestion {
		t.Fatalf("global search did not return the question: %#v", search)
	}

	var updated Record
	requestJSON(t, client, http.MethodPatch, server.URL+"/api/records/"+questionSet.ID, map[string]any{
		"priority": "high",
	}, http.StatusOK, &updated)
	if updated.Priority != "high" {
		t.Fatalf("updated priority = %q, want high", updated.Priority)
	}
}

func TestCollaborationHierarchyActivityAndSuggestion(t *testing.T) {
	store, err := OpenStore(filepath.Join(t.TempDir(), "collaboration.db"))
	if err != nil {
		t.Fatalf("open store: %v", err)
	}
	defer store.Close()
	server := httptest.NewServer(NewServer(store, Config{SessionLifetime: 24 * 60 * 60 * 1e9}))
	defer server.Close()
	ownerClient := testClient(t)
	partnerClient := testClient(t)
	owner := register(t, ownerClient, server.URL, "owner@example.test", "owner")
	partner := register(t, partnerClient, server.URL, "partner@example.test", "partner")

	root := createRecord(t, ownerClient, server.URL, map[string]any{
		"type": "goal", "title": "Развитие платформы", "ownerId": owner.ID,
		"workstream": "platform", "priority": "high", "isRoot": true,
	})
	if root.Workstream != "platform" || root.Priority != "high" || !root.IsRoot {
		t.Fatalf("root classification = %#v", root)
	}
	privateTask := createRecord(t, ownerClient, server.URL, map[string]any{
		"type": "task", "title": "Личная проверка архитектуры", "ownerId": owner.ID,
		"workstream": "platform", "editPolicy": "owner_only", "parentId": root.ID,
		"estimateMinutes": 60, "actualMinutes": 20,
	})
	if privateTask.ParentID == nil || *privateTask.ParentID != root.ID || privateTask.EditPolicy != "owner_only" || privateTask.ActualMinutes != 20 {
		t.Fatalf("private task hierarchy = %#v", privateTask)
	}
	requestJSON(t, partnerClient, http.MethodPatch, server.URL+"/api/records/"+privateTask.ID, map[string]any{
		"progress": 40, "expectedUpdatedAt": privateTask.UpdatedAt,
	}, http.StatusForbidden, nil)
	requestJSON(t, partnerClient, http.MethodPost, server.URL+"/api/records/"+privateTask.ID+"/proofs", map[string]any{
		"kind": "text", "content": "Попытка изменить личную задачу",
	}, http.StatusForbidden, nil)

	sharedTask := createRecord(t, ownerClient, server.URL, map[string]any{
		"type": "task", "title": "Общий прогон мобильного интерфейса", "ownerId": owner.ID,
		"workstream": "platform", "editPolicy": "shared", "parentId": root.ID, "estimateMinutes": 90,
	})
	var sharedUpdated Record
	requestJSON(t, partnerClient, http.MethodPatch, server.URL+"/api/records/"+sharedTask.ID, map[string]any{
		"progress": 50, "progressNote": "Проверена половина сценариев", "expectedUpdatedAt": sharedTask.UpdatedAt,
	}, http.StatusOK, &sharedUpdated)
	if sharedUpdated.Progress != 50 {
		t.Fatalf("shared task update = %#v", sharedUpdated)
	}
	requestJSON(t, partnerClient, http.MethodPatch, server.URL+"/api/records/"+sharedTask.ID, map[string]any{
		"editPolicy": "owner_only", "expectedUpdatedAt": sharedUpdated.UpdatedAt,
	}, http.StatusForbidden, nil)
	var sharedProofs []Proof
	requestJSON(t, partnerClient, http.MethodPost, server.URL+"/api/records/"+sharedTask.ID+"/proofs", map[string]any{
		"kind": "text", "content": "Проверены мобильные диалоги",
	}, http.StatusCreated, &sharedProofs)
	requestJSON(t, partnerClient, http.MethodPost, server.URL+"/api/records/"+sharedTask.ID+"/complete", map[string]any{
		"result": "Мобильный прогон завершён",
	}, http.StatusOK, &sharedUpdated)

	requestJSON(t, ownerClient, http.MethodPatch, server.URL+"/api/records/"+root.ID, map[string]any{
		"parentId": privateTask.ID, "expectedUpdatedAt": root.UpdatedAt,
	}, http.StatusBadRequest, nil)
	var promoted Record
	requestJSON(t, ownerClient, http.MethodPatch, server.URL+"/api/records/"+privateTask.ID, map[string]any{
		"isRoot": true, "expectedUpdatedAt": privateTask.UpdatedAt,
	}, http.StatusOK, &promoted)
	if !promoted.IsRoot || promoted.ParentID != nil {
		t.Fatalf("promoted root = %#v", promoted)
	}

	requestJSON(t, partnerClient, http.MethodPost, server.URL+"/api/presence", map[string]any{
		"activeSeconds": 45, "interactions": 12,
	}, http.StatusNoContent, nil)
	var profile UserProfile
	requestJSON(t, ownerClient, http.MethodGet, server.URL+"/api/users/"+strconv.FormatInt(partner.ID, 10)+"/profile", nil, http.StatusOK, &profile)
	if profile.ActiveSeconds30Days != 45 || profile.Interactions30Days != 12 || len(profile.Activity) != 1 {
		t.Fatalf("partner activity profile = %#v", profile)
	}

	var suggestion RecordSuggestion
	requestJSON(t, ownerClient, http.MethodPost, server.URL+"/api/ai/suggest-record", map[string]any{
		"type": "task", "title": "Критичный баг интерфейса платформы",
	}, http.StatusOK, &suggestion)
	if suggestion.Priority != "critical" || suggestion.Workstream != "platform" || suggestion.Source != "heuristic" {
		t.Fatalf("heuristic suggestion = %#v", suggestion)
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

func requestGetJSONWithHeaders(t *testing.T, client *http.Client, url string, target any) http.Header {
	t.Helper()
	request, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		t.Fatalf("create request: %v", err)
	}
	response, err := client.Do(request)
	if err != nil {
		t.Fatalf("request GET %s: %v", url, err)
	}
	defer response.Body.Close()
	responseBody, _ := io.ReadAll(response.Body)
	if response.StatusCode != http.StatusOK {
		t.Fatalf("GET %s status=%d want=%d body=%s", url, response.StatusCode, http.StatusOK, responseBody)
	}
	if err := json.Unmarshal(responseBody, target); err != nil {
		t.Fatalf("decode response %s: %v; body=%s", url, err, responseBody)
	}
	return response.Header.Clone()
}
