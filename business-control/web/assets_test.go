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

func TestObjectFirstWorkflowAssetsAreEmbedded(t *testing.T) {
	app, err := Files.ReadFile("app.js")
	if err != nil {
		t.Fatalf("read app.js: %v", err)
	}
	for _, marker := range [][]byte{
		[]byte("function navigateToView"),
		[]byte("Правила и критерии"),
		[]byte("data-create-output"),
		[]byte("Продолжить цепочку"),
		[]byte("function renderGraph"),
		[]byte("function renderWorkList"),
		[]byte("function runGlobalSearch"),
	} {
		if !bytes.Contains(app, marker) {
			t.Fatalf("app.js does not contain object-first workflow marker %q", marker)
		}
	}
	if _, err := Files.ReadFile("fonts/Inter-Regular.woff2"); err != nil {
		t.Fatalf("embedded Inter font missing: %v", err)
	}
	if library, err := Files.ReadFile("vendor/cytoscape-3.34.1.min.js"); err != nil || len(library) < 400_000 {
		t.Fatalf("embedded Cytoscape library missing or incomplete: bytes=%d err=%v", len(library), err)
	}
	if _, err := Files.ReadFile("vendor/CYTOSCAPE-LICENSE.txt"); err != nil {
		t.Fatalf("embedded Cytoscape license missing: %v", err)
	}
}
