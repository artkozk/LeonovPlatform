package app

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"time"

	"leonovcare/backend/internal/config"
	dbmigrate "leonovcare/backend/internal/db"
	"leonovcare/backend/internal/judge"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"
)

type App struct {
	Cfg        config.Config
	DB         *pgxpool.Pool
	Redis      *redis.Client
	Log        *slog.Logger
	Judge      judge.Engine
	SupportHub *SupportHub
}

type UserContext struct {
	ID       string
	Role     string
	PlanCode string
}

type QueueJob struct {
	SubmissionID string `json:"submissionId"`
}

type APIError struct {
	Error     string `json:"error"`
	Details   string `json:"details,omitempty"`
	RequestID string `json:"requestId,omitempty"`
}

func New(ctx context.Context, cfg config.Config, logger *slog.Logger) (*App, error) {
	db, err := pgxpool.New(ctx, cfg.DBURL)
	if err != nil {
		return nil, fmt.Errorf("connect db: %w", err)
	}
	if err := db.Ping(ctx); err != nil {
		return nil, fmt.Errorf("ping db: %w", err)
	}
	if cfg.EnableAutoMigrate {
		migrationsDir := "migrations"
		if _, err := os.Stat(migrationsDir); os.IsNotExist(err) {
			migrationsDir = filepath.Join("backend", "migrations")
		}
		if err := dbmigrate.ApplyMigrations(ctx, db, migrationsDir); err != nil {
			return nil, fmt.Errorf("apply migrations: %w", err)
		}
	}

	redisOpts, err := redis.ParseURL(cfg.RedisURL)
	if err != nil {
		return nil, fmt.Errorf("parse redis url: %w", err)
	}
	rds := redis.NewClient(redisOpts)
	if err := rds.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("ping redis: %w", err)
	}

	j := judge.NewJavaEngine(cfg.JavaTimeoutSeconds, cfg.JudgeMode)

	return &App{
		Cfg:        cfg,
		DB:         db,
		Redis:      rds,
		Log:        logger,
		Judge:      j,
		SupportHub: NewSupportHub(),
	}, nil
}

func (a *App) Close() {
	if a.Redis != nil {
		_ = a.Redis.Close()
	}
	if a.DB != nil {
		a.DB.Close()
	}
}

func jsonMarshal(v any) string {
	b, _ := json.Marshal(v)
	return string(b)
}

func nowUTC() time.Time {
	return time.Now().UTC()
}
