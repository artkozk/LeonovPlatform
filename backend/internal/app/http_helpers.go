package app

import (
	"database/sql"
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
)

func badRequest(c *gin.Context, err error) {
	c.JSON(http.StatusBadRequest, APIError{Error: "bad request", Details: err.Error()})
}

func unauthorized(c *gin.Context, msg string) {
	c.JSON(http.StatusUnauthorized, APIError{Error: msg})
}

func internalServerError(c *gin.Context, err error) {
	c.JSON(http.StatusInternalServerError, APIError{Error: "internal server error", Details: err.Error()})
}

func notFound(c *gin.Context, msg string) {
	c.JSON(http.StatusNotFound, APIError{Error: msg})
}

func isNoRows(err error) bool {
	return errors.Is(err, sql.ErrNoRows)
}
