package security

import (
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
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

func TestParseTokenRejectsUnexpectedSigningMethod(t *testing.T) {
	claims := TokenClaims{
		UserID: "user-1",
		Role:   "student",
		Type:   "access",
		RegisteredClaims: jwt.RegisteredClaims{
			ID:        "test-jti",
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Minute)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS512, claims)
	raw, err := token.SignedString([]byte("secret"))
	if err != nil {
		t.Fatalf("sign token: %v", err)
	}

	if _, err := ParseToken(raw, "secret"); err == nil {
		t.Fatalf("expected parse to fail for HS512 token")
	}
}
