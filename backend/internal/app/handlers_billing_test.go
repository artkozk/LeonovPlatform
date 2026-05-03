package app

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"strings"
	"testing"

	"leonovcare/backend/internal/config"
)

func TestNormalizePaymentStatus(t *testing.T) {
	cases := map[string]string{
		"SUCCESS":   "paid",
		"overpaid":  "paid",
		"UNDERPAID": "underpaid",
		"PROCESS":   "processing",
		"NEW":       "pending",
		"FAIL":      "failed",
		"Refunded":  "refunded",
	}

	for input, expected := range cases {
		actual := normalizePaymentStatus(input)
		if actual != expected {
			t.Fatalf("status mapping failed for %q: got %q want %q", input, actual, expected)
		}
	}
}

func TestVerifyCardlinkFormSignature(t *testing.T) {
	token := "secret-token"
	outSum := "380.55"
	invID := "order-123"

	plain := outSum + ":" + invID + ":" + token
	sum := md5.Sum([]byte(plain))
	signature := strings.ToUpper(hex.EncodeToString(sum[:]))

	a := &App{
		Cfg: config.Config{
			CardlinkAPIToken: token,
		},
	}

	if err := a.verifyCardlinkFormSignature(outSum, invID, signature); err != nil {
		t.Fatalf("expected valid signature, got error: %v", err)
	}
	if err := a.verifyCardlinkFormSignature(outSum, invID, "WRONG_SIGNATURE"); err == nil {
		t.Fatalf("expected invalid signature error")
	}
}

func TestParseCardlinkProviderError(t *testing.T) {
	raw := `cardlink create bill status 403: {"success":false,"message":"api:error.ip_access_denied","errors":{"ip":"85.198.82.221"}}`
	msg, ip := parseCardlinkProviderError(raw)
	if msg != "api:error.ip_access_denied" {
		t.Fatalf("unexpected provider message: %q", msg)
	}
	if ip != "85.198.82.221" {
		t.Fatalf("unexpected blocked ip: %q", ip)
	}
}

func TestClassifyCardlinkCreateBillIssueIPDenied(t *testing.T) {
	a := &App{
		Cfg: config.Config{
			CardlinkShopID: "G8vrpjx2LR",
		},
	}
	err := fmt.Errorf(`cardlink create bill status 403: {"success":false,"message":"api:error.ip_access_denied","errors":{"ip":"85.198.82.221"}}`)

	blocked, details, missing := a.classifyCardlinkCreateBillIssue(err)
	if !blocked {
		t.Fatalf("expected provider issue to be marked as blocked")
	}
	if !strings.Contains(details, "85.198.82.221") {
		t.Fatalf("details must include blocked ip, got: %q", details)
	}
	if !strings.Contains(details, "G8vrpjx2LR") {
		t.Fatalf("details must include shop id, got: %q", details)
	}
	if len(missing) == 0 {
		t.Fatalf("expected missing checklist to be returned")
	}
}
