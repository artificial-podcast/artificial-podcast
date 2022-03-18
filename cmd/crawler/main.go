package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"github.com/artificial-podcast/artificial-podcast/pkg/crawler"
	"github.com/txsvc/stdlib/v2/timestamp"
)

const (
	minLineLength = 5

	//startToken   = "<|startoftext|>"
	//endToken     = "<|endoftext|>"
	startToken   = ""
	endToken     = "\n"
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

func merge(path string) error {

	// create and open the merge file

	merge_file := fmt.Sprintf("%s/merge_%d.txt", path, timestamp.Now())
	out, err := os.OpenFile(merge_file, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer out.Close()

	// scan the dir for files to merge into
	files, err := ioutil.ReadDir(path)
	if err != nil {
		log.Fatal(err)
	}

	for _, f := range files {
		if strings.HasSuffix(f.Name(), ".training.txt") {
			full_path := fmt.Sprintf("%s/%s", path, f.Name())

			merge, err := os.Open(full_path)
			if err != nil {
				log.Fatal(err)
			}
			defer merge.Close()

			_, err = io.Copy(out, merge)
			if err != nil {
				log.Fatal(err)
			}
		}
	}
	return nil
}

func process(id, path string) error {
	source := fmt.Sprintf("%s/%s.txt", path, id)
	output := fmt.Sprintf("%s/%s.training.txt", path, id)

	if _, err := os.Stat(source); errors.Is(err, os.ErrNotExist) {
		if err := crawler.RetrieveFromAO3(id, source); err != nil {
			return err
		}
	}

	l, err := clean_rewrite(source, output)
	if err != nil {
		return err
	}

	fmt.Printf("Retrieved '%s'. Length=%d characters.\n", output, l)

	return nil
}

func main() {
	if len(os.Args) != 3 {
		log.Fatal(fmt.Errorf("invalid arguments"))
	}

	input := os.Args[1]
	path := os.Args[2]

	if strings.HasSuffix(input, ".txt") {
		file, err := os.Open(input)
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()

		// read id's from the input file and retrieve the texts
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			id := scanner.Text()

			if err := process(id, path); err != nil {
				log.Fatal(err)
			}
		}

		// merge all the texts
		if err := merge(path); err != nil {
			log.Fatal(err)
		}

	} else {
		if err := process(input, path); err != nil {
			log.Fatal(err)
		}
	}
}
