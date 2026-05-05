package app

import "testing"

func TestEnsureIDEPluginRequiredFilesAddsMissingReadme(t *testing.T) {
	policy := `{"checker_type":"ide_plugin","checker":{"required_files":["main.py","README.md"]}}`
	files := []submissionFilePayload{
		{Path: "main.py", Content: "print('ok')\n"},
	}

	got := ensureIDEPluginRequiredFiles(
		files,
		"print('ok')\n",
		policy,
		"python",
		"Следующий год",
		"main.py",
		"# starter\n",
	)

	if len(got) != 2 {
		t.Fatalf("expected 2 files, got %d", len(got))
	}

	var hasMain bool
	var hasReadme bool
	for _, file := range got {
		if file.Path == "main.py" {
			hasMain = true
		}
		if file.Path == "README.md" {
			hasReadme = true
			if file.Content == "" {
				t.Fatalf("expected README.md content to be prefilled")
			}
		}
	}
	if !hasMain || !hasReadme {
		t.Fatalf("expected main.py and README.md, got %#v", got)
	}
}

func TestEnsureIDEPluginRequiredFilesAddsMainWhenOnlySourceProvided(t *testing.T) {
	policy := `{"checker_type":"ide_plugin","checker":{"required_files":["main.py","README.md"]}}`
	got := ensureIDEPluginRequiredFiles(
		nil,
		"print('ready')\n",
		policy,
		"python",
		"Следующий год",
		"main.py",
		"# starter\n",
	)

	if len(got) != 2 {
		t.Fatalf("expected 2 files, got %d", len(got))
	}
	if got[0].Path != "main.py" && got[1].Path != "main.py" {
		t.Fatalf("expected main.py in files, got %#v", got)
	}
}

