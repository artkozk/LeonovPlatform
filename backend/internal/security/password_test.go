package security

import "testing"

func TestPasswordHashing(t *testing.T) {
	h, err := HashPassword("StrongPassword123!")
	if err != nil {
		t.Fatalf("hash failed: %v", err)
	}
	if !CheckPassword(h, "StrongPassword123!") {
		t.Fatal("password check should pass")
	}
	if CheckPassword(h, "wrong") {
		t.Fatal("password check should fail")
	}
}
