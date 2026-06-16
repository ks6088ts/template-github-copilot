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
	"github.com/spf13/cobra"
)

// tutorialCmd represents the tutorial command group.
//
// It mirrors the Python tutorial scripts under
// src/python/scripts/tutorials/ as Go subcommands built on the
// GitHub Copilot SDK for Go (github.com/github/copilot-sdk/go).
var tutorialCmd = &cobra.Command{
	Use:   "tutorial",
	Short: "Copilot SDK tutorial subcommands",
	Long: `Tutorial subcommands that demonstrate the GitHub Copilot SDK for Go.

Each subcommand corresponds 1:1 to a Python tutorial script under
src/python/scripts/tutorials/. Running these subcommands requires the
GitHub Copilot CLI to be installed and authenticated.`,
}

// GetCommand returns the tutorial parent command for registration on the root command.
func GetCommand() *cobra.Command {
	return tutorialCmd
}
