package tutorial

import (
	"os"
	"testing"
)

func TestParseOptionalBool(t *testing.T) {
	tests := []struct {
		name  string
		value string
		want  bool
		ok    bool
	}{
		{name: "empty", value: "", want: false, ok: false},
		{name: "true", value: "true", want: true, ok: true},
		{name: "python truthy", value: "yes", want: true, ok: true},
		{name: "false", value: "false", want: false, ok: true},
		{name: "python falsey", value: "off", want: false, ok: true},
		{name: "invalid", value: "maybe", want: false, ok: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, ok := parseOptionalBool(tt.value)
			if got != tt.want || ok != tt.ok {
				t.Fatalf("parseOptionalBool(%q) = (%v, %v), want (%v, %v)", tt.value, got, ok, tt.want, tt.ok)
			}
		})
	}
}

func TestTelemetryConfigDisabledWithoutEndpoint(t *testing.T) {
	restore := overrideTelemetryOptions("", "", "")
	defer restore()

	if cfg := telemetryConfig(); cfg != nil {
		t.Fatalf("telemetryConfig() = %#v, want nil", cfg)
	}
}

func TestTelemetryConfigFromOptions(t *testing.T) {
	t.Setenv(otelBSPDelayEnv, "")
	restore := overrideTelemetryOptions("http://localhost:4318", "yes", "500")
	defer restore()

	cfg := telemetryConfig()
	if cfg == nil {
		t.Fatal("telemetryConfig() = nil, want config")
	}
	if cfg.OTLPEndpoint != "http://localhost:4318" {
		t.Fatalf("OTLPEndpoint = %q, want %q", cfg.OTLPEndpoint, "http://localhost:4318")
	}
	if cfg.ExporterType != "otlp-http" {
		t.Fatalf("ExporterType = %q, want %q", cfg.ExporterType, "otlp-http")
	}
	if cfg.CaptureContent == nil || !*cfg.CaptureContent {
		t.Fatalf("CaptureContent = %#v, want true", cfg.CaptureContent)
	}
	if got := os.Getenv(otelBSPDelayEnv); got != "500" {
		t.Fatalf("%s = %q, want %q", otelBSPDelayEnv, got, "500")
	}
}

func TestValidateTelemetryOptions(t *testing.T) {
	restore := overrideTelemetryOptions("", "maybe", "")
	defer restore()

	if err := validateTelemetryOptions(); err == nil {
		t.Fatal("validateTelemetryOptions() = nil, want error")
	}

	tutorialOTELCaptureContent = "false"
	if err := validateTelemetryOptions(); err != nil {
		t.Fatalf("validateTelemetryOptions() = %v, want nil", err)
	}
}

func overrideTelemetryOptions(endpoint, captureContent, scheduleDelay string) func() {
	previousEndpoint := tutorialOTELEndpoint
	previousCaptureContent := tutorialOTELCaptureContent
	previousScheduleDelay := tutorialOTELBSPScheduleDelay

	tutorialOTELEndpoint = endpoint
	tutorialOTELCaptureContent = captureContent
	tutorialOTELBSPScheduleDelay = scheduleDelay

	return func() {
		tutorialOTELEndpoint = previousEndpoint
		tutorialOTELCaptureContent = previousCaptureContent
		tutorialOTELBSPScheduleDelay = previousScheduleDelay
	}
}
