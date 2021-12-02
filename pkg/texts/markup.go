package texts

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/jdkato/prose/v2"
)

var (
	tags TagStack = make(TagStack, 0) // FIXME THIS MAKES THE ENTIRE THING NOT THREAD-SAFE!!!!
)

func MarkupText(source, output string) error {
	src, err := os.Open(source)
	if err != nil {
		return err
	}
	defer src.Close()

	scanner := bufio.NewScanner(src)
	var builder strings.Builder

	err = Markup(scanner, &builder)
	if err != nil {
		return err
	}

	// only create the output file once we know the Markup process succeded
	dst, err := os.Create(output)
	if err != nil {
		return err
	}
	writer := bufio.NewWriter(dst)

	defer func() {
		writer.Flush()
		dst.Close()
	}()

	_, err = writer.WriteString(builder.String())
	return err
}

func Markup(src *bufio.Scanner, ssml *strings.Builder) error {

	// wrap the whole text in <speak></speak>
	tags = tags.Push("speak", ssml)
	defer tags.Pop(ssml)

	// each text is a series of paragraphs
	for src.Scan() {
		line := src.Text()

		// check for markdown headlines
		if isHeadline(line, ssml) {
			continue
		}

		// else, split the text into paragraphs
		var p strings.Builder

		// start a new paragraph

		if len(line) == 0 {
			pp := scanParagraph(src, &p)
			if err := markupParagraph(pp, ssml); err != nil {
				return err
			}
		} else {
			p.WriteString(line)
			pp := scanParagraph(src, &p)
			if err := markupParagraph(pp, ssml); err != nil {
				return err
			}
		}
	}
	if err := src.Err(); err != nil {
		return err
	}
	return nil
}

func markupParagraph(para *strings.Builder, ssml *strings.Builder) error {
	doc, err := prose.NewDocument(para.String(), prose.WithExtraction(false))
	if err != nil {
		return err
	}

	tags = tags.Push("p", ssml)
	defer func() {
		tags = tags.Pop(ssml)
	}()

	for _, sent := range doc.Sentences() {
		nl := escapeLine(cleanupLine(sent.Text))
		ssml.WriteString(nl + "\n")

		fmt.Println(nl)
		fmt.Println("--")
	}

	return nil
}

func isHeadline(line string, ssml *strings.Builder) bool {
	if strings.HasPrefix(line, "#") {
		i := strings.Index(line, " ")
		if i != -1 {
			if i == 1 {
				ssml.WriteString(fmt.Sprintf("\n%s<break strength=\"x-strong\"/>\n", line[i+1:]))
			} else {
				ssml.WriteString(fmt.Sprintf("\n%s<break strength=\"strong\"/>\n", line[i+1:]))
			}
		} else {
			ssml.WriteString("\n<break strength=\"x-strong\"/>\n")
		}
		return true
	}
	return false
}

func scanParagraph(src *bufio.Scanner, para *strings.Builder) *strings.Builder {
	for src.Scan() {
		line := src.Text()
		if len(line) == 0 { // read lines until an empty line
			break
		}
		para.WriteString(line)
	}
	return para
}

func cleanupLine(txt string) string {
	l := strings.ReplaceAll(txt, "\n", "")
	l = strings.ReplaceAll(l, "“", "\"")
	l = strings.ReplaceAll(l, "”", "\"")
	return l
}

// escapeLine replaces reserved characters with their escaped equivalents.
// See https://docs.aws.amazon.com/polly/latest/dg/escapees.html for details
func escapeLine(txt string) string {
	l := strings.ReplaceAll(txt, "&", "&amp;") // THIS HAS TO BE FIRST !
	l = strings.ReplaceAll(l, "\"", "&quot;")
	l = strings.ReplaceAll(l, "'", "&apos;")
	l = strings.ReplaceAll(l, "<", "&lt;")
	l = strings.ReplaceAll(l, ">", "&gt;")
	return l
}
