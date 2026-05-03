package seed

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

// EnsureDemoCourse intentionally does nothing for launch configuration.
// Demo Java content is removed from the production path.
func EnsureDemoCourse(_ context.Context, _ *pgxpool.Pool) error {
	return nil
}
