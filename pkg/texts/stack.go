package texts

import (
	"fmt"
	"strings"
)

type TagStack []string

func (s TagStack) Push(tag string, dst *strings.Builder) TagStack {
	dst.WriteString(fmt.Sprintf("<%s>\n", tag))
	return append(s, tag)
}

func (s TagStack) Pop(dst *strings.Builder) TagStack {
	l := len(s)
	if l == 0 {
		return s
	}

	tag := s[l-1]
	dst.WriteString(fmt.Sprintf("</%s>\n", tag))

	return s[:l-1]
}
