package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/urfave/cli/v2"

	artificialpodcast "github.com/artificial-podcast/artificial-podcast"
	"github.com/artificial-podcast/artificial-podcast/pkg/synth"
	"github.com/artificial-podcast/artificial-podcast/pkg/texts"
)

const (
	cmdLineName = "ap"

	globalHelpText = `Artificial Podcast: A set of tools to create podcast audio files.

To see the full list of supported commands, run 'ap help'`
)

var (
	MsgMissingCmdParameters = "missing parameter(s). try 'ap help %s'"
	MsgInvalidCmdParameters = "unknown sub-command '%s'. try 'ap help %s'"
)

func main() {

	app := &cli.App{
		Name:     cmdLineName,
		Version:  artificialpodcast.VersionString,
		Usage:    fmt.Sprintf("Artificial Podcast CLI (%s)", artificialpodcast.Version),
		Commands: setupCommands(),
		Action: func(c *cli.Context) error {
			fmt.Println(globalHelpText)
			return nil
		},
	}

	sort.Sort(cli.FlagsByName(app.Flags))

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}

func cmdCreateSSML(c *cli.Context) error {
	if c.NArg() < 1 {
		printError(c, fmt.Errorf(MsgMissingCmdParameters, c.Command.Name))
		return nil
	}

	src := c.Args().First()
	dest := ""
	if c.NArg() > 1 {
		dest = c.Args().Get(1)
	} else {
		filename := filepath.Base(src)
		parts := strings.Split(filename, ".")
		dest = filepath.Join(filepath.Dir(src), fmt.Sprintf("%s.ssml", parts[0]))
	}

	err := texts.MarkupText(src, dest)
	if err != nil {
		printError(c, err)
	}
	return nil
}

func cmdCreateAudio(c *cli.Context) error {
	if c.NArg() < 1 {
		printError(c, fmt.Errorf(MsgMissingCmdParameters, c.Command.Name))
		return nil
	}

	src := c.Args().First()
	dest := ""
	if c.NArg() > 1 {
		dest = c.Args().Get(1)
	} else {
		filename := filepath.Base(src)
		parts := strings.Split(filename, ".")
		dest = filepath.Join(filepath.Dir(src), fmt.Sprintf("%s.mp3", parts[0]))
	}

	printMsg("creating audio from %s", src)

	ctx := context.Background()
	err := synth.SynthesizeSSML(ctx, src, dest, "Amy")
	if err != nil {
		printError(c, err)
		return nil
	}

	printMsg("created %s", dest)
	return nil
}

func setupCommands() []*cli.Command {
	c := []*cli.Command{
		{
			Name:      "ssml",
			Usage:     "Create SSML from markup text",
			UsageText: "ssml SRC [DEST]",
			Action:    cmdCreateSSML,
		},
		{
			Name:      "audio",
			Usage:     "Create audio file from SSML text",
			UsageText: "audio SRC [DEST]",
			Action:    cmdCreateAudio,
		},
	}
	return c
}

func boolFlag(c *cli.Context, flag string) bool {
	value := c.String(flag)

	if value != "" {
		if strings.ToLower(value) == "true" {
			return true
		}
	}
	return false
}

// printError formats a CLI error and prints it
func printError(c *cli.Context, err error) {
	fmt.Printf("%s '%s': %v\n", cmdLineName, c.Command.Name, strings.ToLower(err.Error()))
}

// printMsg is used for all the cli output
func printMsg(format string, a ...interface{}) {
	fmt.Printf(format+"\n", a...)
}
