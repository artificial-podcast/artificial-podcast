package texts

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

const (
	source = "../../examples/texts/text3.md"
	output = "../../examples/texts/text3.ssml"
)

func TestMarkupText(t *testing.T) {
	err := MarkupText(source, output)
	assert.NoError(t, err)
}
