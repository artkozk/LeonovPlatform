package main

import (
	"context"
	"log"
	"os"
	"path/filepath"

	"leonovcare/backend/internal/config"
	"leonovcare/backend/internal/db"

	"github.com/jackc/pgx/v5/pgxpool"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("load config: %v", err)
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, cfg.DBURL)
	if err != nil {
		log.Fatalf("connect db: %v", err)
	}
	defer pool.Close()

	if err := pool.Ping(ctx); err != nil {
		log.Fatalf("ping db: %v", err)
	}

	migrationsDir := "migrations"
	if _, err := os.Stat(migrationsDir); os.IsNotExist(err) {
		migrationsDir = filepath.Join("backend", "migrations")
	}

	if err := db.ApplyMigrations(ctx, pool, migrationsDir); err != nil {
		log.Fatalf("apply migrations: %v", err)
	}

	log.Printf("migrations applied successfully from %s", migrationsDir)
}
