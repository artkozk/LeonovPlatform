package web

import (
	"bytes"
	"testing"
)

func TestProgressIndicatorsDoNotRequireInlineStyles(t *testing.T) {
	app, err := Files.ReadFile("app.js")
	if err != nil {
		t.Fatalf("read app.js: %v", err)
	}
	if bytes.Contains(app, []byte(`style="width:`)) {
		t.Fatal("progress indicators must not use inline widths because the production CSP blocks inline styles")
	}
	if !bytes.Contains(app, []byte(`<progress`)) {
		t.Fatal("progress indicators must use native progress values")
	}
}
