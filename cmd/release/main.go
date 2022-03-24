package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/rand"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"gopkg.in/yaml.v3"

	"github.com/artificial-podcast/artificial-podcast/pkg/synth"
	"github.com/artificial-podcast/artificial-podcast/pkg/texts"
	"github.com/podops/podops"
	"github.com/podops/podops/config"
	"github.com/podops/podops/feed"
)

// tool working_dir path_to_story episode_number
// go run main.go ../../examples/show ../../examples/show/generated/episode1.md 1

func main() {
	if len(os.Args) != 4 {
		log.Fatal(fmt.Errorf("invalid arguments"))
	}

	workingDir := os.Args[1]
	sourceFilePath := os.Args[2]
	episode, err := strconv.Atoi(os.Args[3])
	if err != nil {
		log.Fatal(err)
	}

	// find and load the show.yaml
	showPath := filepath.Join(workingDir, feed.DefaultShowName)
	data, err := ioutil.ReadFile(showPath)
	if err != nil {
		log.Fatal(err)
	}

	rsrc, parentGUID, err := loadShowResource(data)
	if err != nil {
		log.Fatal(err)
	}

	// convert and validate show.yaml
	show := rsrc.(*podops.Show)
	cfg, _ := config.LoadClientSettings("")

	// generate the SSML
	ssmlFileName := fmt.Sprintf("episode%d.ssml", episode)
	ssmlFilePath := filepath.Join(workingDir, "assets", ssmlFileName)
	err = texts.MarkupText(sourceFilePath, ssmlFilePath, false)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf(" --> Created SSML %s\n", ssmlFileName)

	// prepare assetPath
	audioFileName := fmt.Sprintf("episode%d.mp3", episode)
	audioFilePath := filepath.Join(workingDir, "assets", audioFileName)

	// create the audio
	fmt.Printf(" --> Waiting for MP3 %s\n", audioFileName)
	ctx := context.Background()
	err = synth.SynthesizeSSML(ctx, ssmlFilePath, audioFilePath, synth.VoiceId("default"), true)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf(" --> Created MP3 %s\n", audioFileName)

	// create the episode yaml
	episodeName := fmt.Sprintf("episode%d", episode)
	episodeFileName := fmt.Sprintf("episode%d.yaml", episode)
	episodeFilePath := filepath.Join(workingDir, episodeFileName)

	episodeDoc := podops.DefaultEpisode(episodeName, show.Metadata.Name, createRandomAssetGUID(), parentGUID, cfg.GetOption(config.PodopsServiceEndpointEnv), cfg.GetOption(config.PodopsContentEndpointEnv))
	episodeDoc.Description.Title = fmt.Sprintf("Episode %d", episode)
	episodeDoc.Enclosure.URI = audioFilePath
	episodeDoc.Metadata.Labels[podops.LabelEpisode] = fmt.Sprintf("%d", episode)
	episodeDoc.Metadata.Labels[podops.LabelExplicit] = "yes"

	// load the generated text
	txt, err := loadGeneratedText(sourceFilePath)
	if err != nil {
		log.Fatal(err)
	}
	// generate a summary if possible
	summary := fmt.Sprintf("Episode %d", episode)
	pos := strings.Index(txt, ".")
	if pos != -1 {
		summary = txt[:pos]
	}
	episodeDoc.Description.Summary = summary
	episodeDoc.Description.EpisodeText = txt

	dumpResource(episodeFilePath, episodeDoc)
	fmt.Printf(" --> Created Episode %s\n", episodeFileName)
}

func loadShowResource(data []byte) (interface{}, string, error) {
	var show podops.Show

	err := yaml.Unmarshal([]byte(data), &show)
	if err != nil {
		return nil, "", err
	}

	return &show, show.GUID(), nil
}

func loadGeneratedText(path string) (string, error) {
	var txtBuilder, frontBuilder strings.Builder

	src, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer src.Close()
	scanner := bufio.NewScanner(src)

	frontmatter := false
	for scanner.Scan() {
		line := scanner.Text()

		// skip the frontmatter
		if strings.HasPrefix(line, "---") {
			frontmatter = true
			for scanner.Scan() {
				_line := scanner.Text()
				if strings.HasPrefix(_line, "---") {
					frontmatter = false
					break // done with the frontmatter
				} else {
					frontBuilder.WriteString(line + "\n")
				}
			}
			if frontmatter {
				return "", fmt.Errorf("malformed frontmatter")
			}
			continue
		}
		txtBuilder.WriteString(line + "\n")
	}
	return txtBuilder.String(), nil
}

func createRandomAssetGUID() string {
	uuid := make([]byte, 6)
	n, err := io.ReadFull(rand.Reader, uuid)
	if n != len(uuid) || err != nil {
		return ""
	}
	uuid[4] = uuid[4]&^0xc0 | 0x80
	uuid[2] = uuid[2]&^0xf0 | 0x40

	return fmt.Sprintf("%x", uuid[0:6])
}

func dumpResource(path string, doc interface{}) error {
	var b bytes.Buffer

	yamlEncoder := yaml.NewEncoder(&b)
	yamlEncoder.SetIndent(2)
	yamlEncoder.Encode(doc)

	return ioutil.WriteFile(path, b.Bytes(), 0644)
}
