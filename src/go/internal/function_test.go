package internal

import (
	"testing"
)

func TestAdd(t *testing.T) {
	// Table Driven Test
	tests := []struct {
		name string
		a    int
		b    int
		want int
	}{
		{name: "nominal case", a: 1, b: 2, want: 3},
		{name: "negative case", a: -1, b: -2, want: -3},
		{name: "zero case", a: 0, b: 0, want: 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := add(tt.a, tt.b)
			if got != tt.want {
				t.Errorf("%s: add(%d, %d) = %d; want %d", tt.name, tt.a, tt.b, got, tt.want)
			}
		})
	}
}
