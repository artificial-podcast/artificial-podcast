package texts

import (
	"bufio"
	"math/rand"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"
)

func CreatePrompts(input string, prompts, avgWords, split int) error {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	// source file
	inFile, err := os.Open(input)
	if err != nil {
		return err
	}
	defer inFile.Close()

	// target file
	pathTo := filepath.Dir(input)
	output := path.Join(pathTo, "prompts.yml")
	f, err := os.Create(output)
	if err != nil {
		return err
	}
	defer f.Close()

	lines := make([]string, prompts)
	idx := 0

	// scan the file and create random prompts

	scanner := bufio.NewScanner(inFile)
	for scanner.Scan() {
		line := scanner.Text()
		if r.Intn(100) <= split {
			parts := strings.Split(line, ".")
			pos := r.Intn(len(parts))
			words := strings.Split(parts[pos], " ")

			if len(words) > avgWords {
				lines[idx] = parts[pos]

				idx++
				if idx == prompts {
					idx = 0
				}
			}
		}
	}

	f.WriteString("prompts: |\n")
	for i := range lines {
		f.WriteString("  " + strings.TrimSpace(lines[i]) + "\n\n")
	}

	return nil
}
