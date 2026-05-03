package security

import (
	"testing"
	"time"
)

func TestJWTLifecycle(t *testing.T) {
	token, err := CreateToken("user-1", "student", "access", "secret", time.Minute)
	if err != nil {
		t.Fatalf("create token: %v", err)
	}
	claims, err := ParseToken(token, "secret")
	if err != nil {
		t.Fatalf("parse token: %v", err)
	}
	if claims.UserID != "user-1" || claims.Role != "student" || claims.Type != "access" {
		t.Fatalf("unexpected claims: %+v", claims)
	}
}
