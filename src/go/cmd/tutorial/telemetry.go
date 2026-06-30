/*
Copyright © 2024 ks6088ts

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
package tutorial

import (
	"fmt"
	"log/slog"
	"os"
	"strings"

	copilot "github.com/github/copilot-sdk/go"
)

const (
	otelEndpointEnv       = "OTEL_EXPORTER_OTLP_ENDPOINT"
	otelCaptureContentEnv = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
	otelBSPDelayEnv       = "OTEL_BSP_SCHEDULE_DELAY"
)

var (
	tutorialOTELEndpoint         = os.Getenv(otelEndpointEnv)
	tutorialOTELCaptureContent   = os.Getenv(otelCaptureContentEnv)
	tutorialOTELBSPScheduleDelay = os.Getenv(otelBSPDelayEnv)
)

// telemetryConfig builds an OpenTelemetry configuration for the Copilot CLI
// process from tutorial flags or environment variables, mirroring the Python
// tutorials' helper while also making the knobs available from the Go CLI.
//
// It returns nil (telemetry disabled) unless an OTLP endpoint is set, so the
// tutorials behave exactly as before when no collector is running.
//
//   - --otel-endpoint / OTEL_EXPORTER_OTLP_ENDPOINT: OTLP HTTP endpoint
//     (e.g. http://localhost:4318).
//   - --otel-capture-content / OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT:
//     optional bool to capture prompt/response content in spans.
//   - --otel-bsp-schedule-delay / OTEL_BSP_SCHEDULE_DELAY: optional batch flush
//     interval in ms for the launched Copilot CLI process.
//
// See: https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry
func telemetryConfig() *copilot.TelemetryConfig {
	endpoint := strings.TrimSpace(tutorialOTELEndpoint)
	if endpoint == "" {
		return nil
	}

	cfg := &copilot.TelemetryConfig{
		OTLPEndpoint: endpoint,
		ExporterType: "otlp-http",
	}

	if captureContent, ok := parseOptionalBool(tutorialOTELCaptureContent); ok {
		cfg.CaptureContent = copilot.Bool(captureContent)
	}
	applyTelemetryEnvironment()

	slog.Debug("OpenTelemetry enabled", "endpoint", endpoint)
	return cfg
}

func validateTelemetryOptions() error {
	captureContent := strings.TrimSpace(tutorialOTELCaptureContent)
	if captureContent == "" {
		return nil
	}
	if _, ok := parseOptionalBool(captureContent); !ok {
		return fmt.Errorf("--otel-capture-content must be true or false, got %q", tutorialOTELCaptureContent)
	}
	return nil
}

func applyTelemetryEnvironment() {
	if delay := strings.TrimSpace(tutorialOTELBSPScheduleDelay); delay != "" {
		_ = os.Setenv(otelBSPDelayEnv, delay)
	}
}

func parseOptionalBool(value string) (bool, bool) {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "":
		return false, false
	case "1", "true", "yes", "on", "y", "t":
		return true, true
	case "0", "false", "no", "off", "n", "f":
		return false, true
	default:
		return false, false
	}
}

// newClientOptions returns ClientOptions wired with telemetry and, when cliURL is
// non-empty, a URI connection to an already-running Copilot CLI runtime.
//
// Tutorials pass the result to copilot.NewClient so telemetry is enabled
// consistently whether they connect over stdio (cliURL == "") or TCP.
func newClientOptions(cliURL string) *copilot.ClientOptions {
	opts := &copilot.ClientOptions{
		Telemetry: telemetryConfig(),
	}
	if cliURL != "" {
		opts.Connection = copilot.URIConnection{URL: cliURL}
	}
	return opts
}
