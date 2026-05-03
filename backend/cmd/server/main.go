package main

import (
	"context"
	"log"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"syscall"
	"time"

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

	router := application.Router()
	srv := &http.Server{
		Addr:              ":" + strconv.Itoa(cfg.HTTPPort),
		Handler:           router,
		ReadHeaderTimeout: 10 * time.Second,
	}

	go func() {
		logger.Info("http server started", "port", cfg.HTTPPort)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("http server failed: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(shutdownCtx); err != nil {
		log.Printf("shutdown error: %v", err)
	}
}
