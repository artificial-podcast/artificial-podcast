package texts

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/jdkato/prose/v2"
)

// see https://docs.aws.amazon.com/polly/latest/dg/what-is.html

type (
	Markup struct {
		tags TagStack
	}
)

func MarkupText(source, output string, verbose bool) error {
	src, err := os.Open(source)
	if err != nil {
		return err
	}
	defer src.Close()

	scanner := bufio.NewScanner(src)
	var builder strings.Builder

	markup := Markup{
		tags: make(TagStack, 0),
	}

	err = markup.ToSSML(scanner, &builder, verbose)
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

func (m *Markup) Push(tag string, dst *strings.Builder) {
	m.tags = m.tags.Push(tag, dst)
}

func (m *Markup) PushWithClosingTag(tag, close string, dst *strings.Builder) {
	m.tags = m.tags.PushWithClosingTag(tag, close, dst)
}

func (m *Markup) Pop(dst *strings.Builder) {
	m.tags = m.
		tags.Pop(dst)
}

func (m *Markup) ToSSML(src *bufio.Scanner, ssml *strings.Builder, verbose bool) error {
	narrator := false
	paragraph := false
	frontmatter := false

	// wrap the whole text in <speak></speak>
	m.Push("speak", ssml)
	defer m.Pop(ssml)

	// each text is a series of paragraphs
	for src.Scan() {
		line := src.Text()
		if len(line) == 0 {
			continue // look for the first non-empty line
		}

		// check for markdown headlines
		if isHeadline(line, ssml) {
			continue
		}

		// check for --- / frontmatter
		if strings.HasPrefix(line, "---") {
			frontmatter = true
			for src.Scan() {
				_line := src.Text()
				if strings.HasPrefix(_line, "---") {
					frontmatter = false
					break // done with the frontmatter
				}
			}
			if frontmatter {
				return fmt.Errorf("malformed frontmatter")
			}
			continue
		}

		// check for ++
		if isNarrator(line) {
			narrator = true
			paragraph = true
			continue
		}
		// check for @@
		if isParagraph(line) {
			paragraph = true
			continue
		}

		// else, split the text into paragraphs
		var p strings.Builder
		var lines int

		p.WriteString(line)
		lines = scan(src, &p)

		if lines == 1 && !paragraph {
			if err := m.sentence(&p, ssml, verbose); err != nil {
				return err
			}
		} else {
			if err := m.paragraph(&p, narrator, ssml, verbose); err != nil {
				return err
			}
		}

		// reset flags at the end of each paragraph
		narrator = false
		paragraph = false
	}
	if err := src.Err(); err != nil {
		return err
	}

	return nil
}

func (m *Markup) paragraph(para *strings.Builder, narrator bool, ssml *strings.Builder, verbose bool) error {
	doc, err := prose.NewDocument(para.String(), prose.WithExtraction(false))
	if err != nil {
		return err
	}

	m.Push("p", ssml)
	if narrator {
		m.PushWithClosingTag("amazon:domain name=\"news\"", "amazon:domain", ssml)
	}
	defer func() {
		m.Pop(ssml)
		if narrator {
			m.Pop(ssml)
		}
	}()

	for _, sent := range doc.Sentences() {
		nl := annotateText(escapeLine(cleanupLine(sent.Text)))
		ssml.WriteString(nl + "\n")

		if verbose {
			fmt.Println(nl)
			fmt.Println("")
		}
	}

	return nil
}

func (m *Markup) sentence(para *strings.Builder, ssml *strings.Builder, verbose bool) error {
	doc, err := prose.NewDocument(para.String(), prose.WithExtraction(false))
	if err != nil {
		return err
	}

	m.Push("s", ssml)

	defer func() {
		m.Pop(ssml)
	}()

	for _, sent := range doc.Sentences() {
		nl := annotateText(escapeLine(cleanupLine(sent.Text)))
		ssml.WriteString(nl + "\n")

		if verbose {
			fmt.Println(nl)
			fmt.Println("")
		}
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

func isNarrator(line string) bool {
	return strings.HasPrefix(line, "++")
}

func isParagraph(line string) bool {
	return strings.HasPrefix(line, "@@")
}

// scan collects lines into a paragraph until an empty line is found
func scan(src *bufio.Scanner, para *strings.Builder) int {
	count := 1 // already one line in the buffer ...

	for src.Scan() {
		line := src.Text()
		if len(line) == 0 { // read lines until an empty line
			break
		}
		para.WriteString(line)
		count++
	}
	return count
}

func cleanupLine(txt string) string {
	l := strings.ReplaceAll(txt, "\n", " ")
	l = strings.ReplaceAll(l, "“", "\"")
	l = strings.ReplaceAll(l, "”", "\"")
	l = strings.ReplaceAll(l, "´", "'")
	l = strings.ReplaceAll(l, ",\"", "\",")

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

func annotateText(txt string) string {
	l := strings.ReplaceAll(txt, ", ", "<break strength=\"weak\"/>")
	l = strings.ReplaceAll(l, ".", "<break strength=\"medium\"/>")

	return l
}
