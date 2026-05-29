package app

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

type quizOptionPayload struct {
	ID   string `json:"id"`
	Text string `json:"text"`
}

type quizQuestionPayload struct {
	ID              string              `json:"id"`
	Question        string              `json:"question"`
	Options         []quizOptionPayload `json:"options"`
	CorrectOptionID string              `json:"correctOptionId"`
}

type quizPayloadEnvelope struct {
	Question        string                `json:"question"`
	Options         []quizOptionPayload   `json:"options"`
	CorrectOptionID string                `json:"correctOptionId"`
	Questions       []quizQuestionPayload `json:"questions"`
	MinScorePercent int                   `json:"minScorePercent"`
}

func sanitizeQuizPayloadForStudent(payload any) any {
	switch typed := payload.(type) {
	case map[string]any:
		next := make(map[string]any, len(typed))
		for key, value := range typed {
			lower := strings.ToLower(strings.TrimSpace(key))
			if lower == "correctoptionid" || lower == "correct_option" {
				continue
			}
			next[key] = sanitizeQuizPayloadForStudent(value)
		}
		return next
	case []any:
		next := make([]any, 0, len(typed))
		for _, value := range typed {
			next = append(next, sanitizeQuizPayloadForStudent(value))
		}
		return next
	default:
		return payload
	}
}

type parsedQuizCheckPayload struct {
	Questions       []quizQuestionPayload
	MinScorePercent int
}

func normalizeQuizMinScorePercent(raw int) int {
	if raw <= 0 {
		return 100
	}
	if raw > 100 {
		return 100
	}
	return raw
}

func parseQuizPayloadForCheck(payloadRaw string) (parsedQuizCheckPayload, error) {
	var envelope quizPayloadEnvelope
	if err := json.Unmarshal([]byte(payloadRaw), &envelope); err != nil {
		return parsedQuizCheckPayload{}, err
	}

	out := make([]quizQuestionPayload, 0)
	if len(envelope.Questions) > 0 {
		for idx, question := range envelope.Questions {
			normalizedID := strings.TrimSpace(question.ID)
			if normalizedID == "" {
				normalizedID = "q" + strconv.Itoa(idx+1)
			}
			out = append(out, quizQuestionPayload{
				ID:              normalizedID,
				Question:        strings.TrimSpace(question.Question),
				Options:         question.Options,
				CorrectOptionID: strings.ToUpper(strings.TrimSpace(question.CorrectOptionID)),
			})
		}
		return parsedQuizCheckPayload{
			Questions:       out,
			MinScorePercent: normalizeQuizMinScorePercent(envelope.MinScorePercent),
		}, nil
	}

	if strings.TrimSpace(envelope.Question) != "" && len(envelope.Options) > 0 {
		out = append(out, quizQuestionPayload{
			ID:              "q1",
			Question:        strings.TrimSpace(envelope.Question),
			Options:         envelope.Options,
			CorrectOptionID: strings.ToUpper(strings.TrimSpace(envelope.CorrectOptionID)),
		})
	}
	return parsedQuizCheckPayload{
		Questions:       out,
		MinScorePercent: normalizeQuizMinScorePercent(envelope.MinScorePercent),
	}, nil
}

func extractQuizQuestionsForCheck(payloadRaw string) ([]quizQuestionPayload, error) {
	parsed, err := parseQuizPayloadForCheck(payloadRaw)
	if err != nil {
		return nil, err
	}
	return parsed.Questions, nil
}

func (a *App) CheckLessonQuiz(c *gin.Context) {
	uctx, ok := userFromContext(c)
	if !ok {
		unauthorized(c, "unauthorized")
		return
	}

	lessonID := strings.TrimSpace(c.Param("lessonID"))
	if _, err := uuid.Parse(lessonID); err != nil {
		badRequest(c, errors.New("lessonID must be uuid"))
		return
	}
	courseID, ok := a.resolveCourseIDByLesson(c, lessonID)
	if !ok {
		return
	}
	if !a.requireCourseAccess(c, uctx.ID, courseID) {
		return
	}

	var req struct {
		BlockID string            `json:"blockId" binding:"required,uuid"`
		Answers map[string]string `json:"answers"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		badRequest(c, err)
		return
	}

	var quizPayloadRaw string
	err := a.DB.QueryRow(c.Request.Context(), `
		SELECT COALESCE(quiz_payload::text, '')
		FROM lesson_blocks
		WHERE id = $1
		  AND lesson_id = $2
		  AND is_published = TRUE
		  AND LOWER(block_type) = 'quiz'
	`, req.BlockID, lessonID).Scan(&quizPayloadRaw)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			notFound(c, "quiz block not found")
			return
		}
		internalServerError(c, err)
		return
	}
	if strings.TrimSpace(quizPayloadRaw) == "" || strings.TrimSpace(quizPayloadRaw) == "null" {
		c.JSON(http.StatusUnprocessableEntity, APIError{Error: "quiz payload is empty"})
		return
	}

	parsed, parseErr := parseQuizPayloadForCheck(quizPayloadRaw)
	questions := parsed.Questions
	if parseErr != nil || len(questions) == 0 {
		c.JSON(http.StatusUnprocessableEntity, APIError{Error: "quiz payload is invalid"})
		return
	}
	minScorePercent := normalizeQuizMinScorePercent(parsed.MinScorePercent)

	failed := make([]string, 0)
	for _, question := range questions {
		id := strings.TrimSpace(question.ID)
		if id == "" {
			continue
		}
		answer := strings.ToUpper(strings.TrimSpace(req.Answers[id]))
		if answer == "" {
			failed = append(failed, id)
			continue
		}
		if answer != strings.ToUpper(strings.TrimSpace(question.CorrectOptionID)) {
			failed = append(failed, id)
		}
	}

	totalQuestions := len(questions)
	correctQuestions := totalQuestions - len(failed)
	scorePercent := 0
	if totalQuestions > 0 {
		scorePercent = int(float64(correctQuestions*100) / float64(totalQuestions))
	}
	isCorrect := correctQuestions*100 >= minScorePercent*totalQuestions

	status := "correct"
	if !isCorrect {
		status = "wrong"
	}

	var progressSnapshot *lessonProgressSnapshot
	if isCorrect {
		if err := a.upsertLessonBlockCompletion(
			c.Request.Context(),
			a.DB,
			uctx.ID,
			lessonID,
			req.BlockID,
			"quiz",
			"",
		); err != nil {
			internalServerError(c, err)
			return
		}
		snapshot, err := a.loadLessonProgressSnapshot(c.Request.Context(), uctx.ID, lessonID)
		if err == nil {
			progressSnapshot = &snapshot
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"status":            status,
		"failedQuestionIds": failed,
		"correctQuestions":  correctQuestions,
		"totalQuestions":    totalQuestions,
		"scorePercent":      scorePercent,
		"minScorePercent":   minScorePercent,
		"progress":          progressSnapshot,
	})
}
