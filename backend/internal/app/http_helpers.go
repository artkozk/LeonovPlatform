package app

import (
	"database/sql"
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
)

const requestIDContextKey = "request_id"

func requestIDFromContext(c *gin.Context) string {
	v, ok := c.Get(requestIDContextKey)
	if !ok {
		return ""
	}
	requestID, ok := v.(string)
	if !ok {
		return ""
	}
	return requestID
}

func badRequest(c *gin.Context, err error) {
	c.JSON(http.StatusBadRequest, APIError{Error: "bad request", Details: err.Error()})
}

func unauthorized(c *gin.Context, msg string) {
	c.JSON(http.StatusUnauthorized, APIError{Error: msg})
}

func internalServerError(c *gin.Context, err error) {
	if err != nil {
		_ = c.Error(err)
	}
	c.JSON(http.StatusInternalServerError, APIError{Error: "internal server error", RequestID: requestIDFromContext(c)})
}

func badGatewayError(c *gin.Context, err error) {
	if err != nil {
		_ = c.Error(err)
	}
	c.JSON(http.StatusBadGateway, APIError{Error: "internal server error", RequestID: requestIDFromContext(c)})
}

func notFound(c *gin.Context, msg string) {
	c.JSON(http.StatusNotFound, APIError{Error: msg})
}

func isNoRows(err error) bool {
	return errors.Is(err, sql.ErrNoRows)
}
