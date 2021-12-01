package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/artificial-podcast/artificial-podcast/pkg/synth"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatal(fmt.Errorf("invalid arguments"))
	}

	input := os.Args[1]
	output := os.Args[2]

	ctx := context.Background()
	err := synth.SynthesizeSSML(ctx, input, output, "Joanna")
	if err != nil {
		log.Fatal(err)
	}
}
