package app

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type googleTokenInfo struct {
	Sub           string `json:"sub"`
	Email         string `json:"email"`
	EmailVerified string `json:"email_verified"`
	Name          string `json:"name"`
	Aud           string `json:"aud"`
	Error         string `json:"error_description"`
}

func (a *App) verifyGoogleIDToken(ctx context.Context, idToken string) (googleTokenInfo, error) {
	idToken = strings.TrimSpace(idToken)
	if idToken == "" {
		return googleTokenInfo{}, fmt.Errorf("id token is empty")
	}

	endpoint := "https://oauth2.googleapis.com/tokeninfo?id_token=" + url.QueryEscape(idToken)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return googleTokenInfo{}, err
	}

	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return googleTokenInfo{}, err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))
	if err != nil {
		return googleTokenInfo{}, err
	}

	var info googleTokenInfo
	if err := json.Unmarshal(raw, &info); err != nil {
		return googleTokenInfo{}, fmt.Errorf("decode google tokeninfo: %w", err)
	}
	if resp.StatusCode >= 300 {
		if info.Error != "" {
			return googleTokenInfo{}, fmt.Errorf("google tokeninfo error: %s", info.Error)
		}
		return googleTokenInfo{}, fmt.Errorf("google tokeninfo status %d", resp.StatusCode)
	}

	if a.Cfg.GoogleClientID != "" && info.Aud != a.Cfg.GoogleClientID {
		return googleTokenInfo{}, fmt.Errorf("google audience mismatch")
	}
	if !strings.EqualFold(strings.TrimSpace(info.EmailVerified), "true") {
		return googleTokenInfo{}, fmt.Errorf("google email is not verified")
	}
	if info.Email == "" || info.Sub == "" {
		return googleTokenInfo{}, fmt.Errorf("google token payload incomplete")
	}

	return info, nil
}

func normalizeGoogleUsername(name, email string) string {
	username := strings.TrimSpace(name)
	if username == "" {
		if i := strings.Index(email, "@"); i > 0 {
			username = email[:i]
		} else {
			username = "google_user"
		}
	}
	username = strings.Map(func(r rune) rune {
		switch {
		case r >= 'a' && r <= 'z':
			return r
		case r >= 'A' && r <= 'Z':
			return r + ('a' - 'A')
		case r >= '0' && r <= '9':
			return r
		case r == '_' || r == '-':
			return r
		case r == ' ' || r == '.':
			return '_'
		default:
			return -1
		}
	}, username)
	if len(username) < 3 {
		username = username + "_lc"
	}
	if len(username) > 32 {
		username = username[:32]
	}
	return username
}
