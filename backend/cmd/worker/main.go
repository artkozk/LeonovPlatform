package main

import (
	"context"
	"log"
	"log/slog"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"

	"leonovcare/backend/internal/app"
	"leonovcare/backend/internal/config"
	"leonovcare/backend/internal/db"
	"leonovcare/backend/internal/seed"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("load config: %v", err)
	}
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
	ctx := context.Background()

	application, err := app.New(ctx, cfg, logger)
	if err != nil {
		log.Fatalf("init app: %v", err)
	}
	defer application.Close()

	if cfg.EnableAutoMigrate {
		migrationsDir := "migrations"
		if _, err := os.Stat(migrationsDir); os.IsNotExist(err) {
			migrationsDir = filepath.Join("backend", "migrations")
		}
		if err := db.ApplyMigrations(ctx, application.DB, migrationsDir); err != nil {
			log.Fatalf("apply migrations: %v", err)
		}
	}
	if cfg.EnableAutoSeed {
		if err := seed.EnsureDemoCourse(ctx, application.DB); err != nil {
			log.Fatalf("seed demo course: %v", err)
		}
	}

	workerCtx, cancel := context.WithCancel(context.Background())
	go func() {
		if err := application.RunSubmissionWorker(workerCtx); err != nil {
			logger.Error("worker stopped", "error", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	cancel()
}
