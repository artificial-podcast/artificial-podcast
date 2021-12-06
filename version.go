package artificialpodcast

import "fmt"

const (
	// Version specifies the verion of the API and its structs
	Version = "v1"

	// MajorVersion of the API
	MajorVersion = 0
	// MinorVersion of the API
	MinorVersion = 3
	// FixVersion of the API
	FixVersion = 0

	// Command line consts
	CommandLineName = "ap"
)

var (
	// VersionString is the canonical API description
	VersionString string = fmt.Sprintf("%d.%d.%d", MajorVersion, MinorVersion, FixVersion)
	// UserAgentString identifies any http request the code makes
	UserAgentString string = fmt.Sprintf("artificial-podcast %d.%d.%d", MajorVersion, MinorVersion, FixVersion)
)
