package main

import (
	"fmt"
	"io/ioutil"
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

	content, err := ioutil.ReadFile(input)
	if err != nil {
		log.Fatal(err)
	}

	err = texts.SynthesizeSSML(string(content), output, "en-GB-Wavenet-F", "en-GB", texts.FEMALE)
	if err != nil {
		log.Fatal(err)
	}
}
