// This was downloaded from the gophercises github:
// https://github.com/gophercises/urlshort/blob/master/main/main.go
// Then edited by me to complete the exercise.
// The bulk of the changes/implementation are the maphandler and YAMLhandler in ../handler.go.
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"urlshortener"
)

var yamlfile *string
var jsonfile *string

var map_sample = map[string]string{
	"/urlshort-godoc": "https://godoc.org/github.com/gophercises/urlshort",
	"/yaml-godoc":     "https://godoc.org/gopkg.in/yaml.v2",
}

var yaml_sample string = `
- path: /urlshort
  url: https://github.com/gophercises/urlshort
- path: /urlshort-final
  url: https://github.com/gophercises/urlshort/tree/solution
`
var json_sample string = `
[
    {
        "path": "/mytest",
        "url": "https://abair.ie/"
    },
    {
        "path": "/mytest-2",
        "url": "https://itaigi.tw/"
    }
]
`

func init() {
	// If a json or yaml file are passed in, reads from them, otherwise uses the default samples above.
	jsonfile = flag.String("json", "", "a .json file to load from")
	yamlfile = flag.String("yaml", "", "a .yaml file to load from")
	flag.Parse()
	if *jsonfile != "" {
		file_to_string(*jsonfile, &json_sample)
		log.Println("Using json file", *jsonfile)
	}
	if *yamlfile != "" {
		file_to_string(*yamlfile, &yaml_sample)
		log.Println("Using yaml file", *yamlfile)
	}
}

func file_to_string(filename string, read_into *string) {
	file, err := os.ReadFile(filename)
	if err != nil {
		panic(err)
	}
	*read_into = string(file)
	// defer file.Close() // not needed for ReadFile
}

func main() {
	mux := defaultMux()

	// Build the MapHandler using the mux as the fallback
	mapHandler := urlshortener.MapHandler(map_sample, mux)

	// Build the YAMLHandler using the mapHandler as the
	// fallback
	yamlHandler, err := urlshortener.YAMLHandler([]byte(yaml_sample), mapHandler)
	if err != nil {
		log.Panic(err)
	}
	// Same with json
	jsonHandler, err := urlshortener.JSONHandler([]byte(json_sample), yamlHandler)
	if err != nil {
		log.Panic(err)
	}
	log.Println("Starting the server on :8080")
	http.ListenAndServe(":8080", jsonHandler)
}

// Default functions provided in the example code.
func defaultMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/", hello)
	return mux
}

func hello(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello, world!")
}
