package app

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
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

func extractQuizQuestionsForCheck(payloadRaw string) ([]quizQuestionPayload, error) {
	var envelope quizPayloadEnvelope
	if err := json.Unmarshal([]byte(payloadRaw), &envelope); err != nil {
		return nil, err
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
		return out, nil
	}

	if strings.TrimSpace(envelope.Question) != "" && len(envelope.Options) > 0 {
		out = append(out, quizQuestionPayload{
			ID:              "q1",
			Question:        strings.TrimSpace(envelope.Question),
			Options:         envelope.Options,
			CorrectOptionID: strings.ToUpper(strings.TrimSpace(envelope.CorrectOptionID)),
		})
	}
	return out, nil
}

func (a *App) CheckLessonQuiz(c *gin.Context) {
	if _, ok := userFromContext(c); !ok {
		unauthorized(c, "unauthorized")
		return
	}

	lessonID := strings.TrimSpace(c.Param("lessonID"))
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

	questions, parseErr := extractQuizQuestionsForCheck(quizPayloadRaw)
	if parseErr != nil || len(questions) == 0 {
		c.JSON(http.StatusUnprocessableEntity, APIError{Error: "quiz payload is invalid"})
		return
	}

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

	status := "correct"
	if len(failed) > 0 {
		status = "wrong"
	}
	c.JSON(http.StatusOK, gin.H{
		"status":            status,
		"failedQuestionIds": failed,
	})
}
