package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/artificial-podcast/artificial-podcast/pkg/crawler"
)

const (
	minLineLength = 5

	startToken   = "<|startoftext|>"
	endToken     = "<|endoftext|>"
	newLineToken = "<|lf|>"
)

var stopWords = []string{"notes:", "summary:", "chapter", "disclaimer:", "http://", "***"}

func clean(s string) (string, int, bool) {
	step1 := strings.Trim(s, " ")

	if len(step1) < minLineLength {
		return "", 0, true
	}

	checks := strings.ToLower(step1)

	for _, word := range stopWords {
		if strings.HasPrefix(checks, word) {
			return "", 0, true
		}
	}

	step2 := strings.ReplaceAll(step1, "***", "")
	step3 := strings.ReplaceAll(step2, "__", "")
	step4 := strings.ReplaceAll(step3, "''", "\" ")

	//return fmt.Sprintf("%s%s%s", startToken, step4, endToken), len(step4), false
	return step4, len(step4), false
}

func clean_rewrite(source, target string) (int, error) {
	n := 0

	reader, err := os.Open(source)
	if err != nil {
		return 0, err
	}

	dst, err := os.Create(target)
	if err != nil {
		return 0, err
	}
	writer := bufio.NewWriter(dst)

	defer func() {
		reader.Close()
		writer.Flush()
		dst.Close()
	}()

	scanner := bufio.NewScanner(reader)
	sentence := false

	for scanner.Scan() {
		line, l, skipped := clean(scanner.Text())
		if !skipped {
			if !sentence {
				writer.WriteString(startToken) // <|startoftext|>
				sentence = true
			}
			writer.WriteString(line)
			n = n + l
		} else {
			if sentence {
				writer.WriteString(fmt.Sprintf("%s\n", endToken)) // <|endoftext|>
				sentence = false
			}
		}
	}
	if sentence {
		writer.WriteString(endToken) // <|endoftext|>
	}

	return n, nil
}

func main() {
	if len(os.Args) != 3 {
		log.Fatal(fmt.Errorf("invalid arguments"))
	}

	id := os.Args[1]
	path := os.Args[2]

	source := fmt.Sprintf("%s/%s.txt", path, id)
	output := fmt.Sprintf("%s/%s.training.txt", path, id)

	err := crawler.RetrieveFromAO3(id, source)
	if err != nil {
		log.Fatal(err)
	}

	l, err := clean_rewrite(source, output)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Retrieved '%s'. Length=%d characters.\n", output, l)
}
