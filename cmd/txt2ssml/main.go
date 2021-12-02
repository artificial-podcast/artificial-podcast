package main

import (
	"fmt"
	"log"
	"os"

	"github.com/artificial-podcast/artificial-podcast/pkg/texts"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatal(fmt.Errorf("invalid arguments"))
	}

	input := os.Args[1]
	output := os.Args[2]

	err := texts.MarkupText(input, output)
	if err != nil {
		log.Fatal(err)
	}
}
