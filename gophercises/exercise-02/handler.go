// This is the primary file for completing gophercises exercise 2.
// Original stub file downloaded from:
// https://github.com/gophercises/urlshort/blob/master/handler.go
package urlshortener

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/go-yaml/yaml"
)

// MapHandler returns an http.HandlerFunc (which is polymophism of http.Handler)
// which maps paths to their corresponding URL.
// If a path is not provided, the fallback handler is called.
func MapHandler(pathsToUrls map[string]string, fallback http.Handler) http.HandlerFunc {
	return func(respwriter http.ResponseWriter, req *http.Request) {
		if realpath, ok := pathsToUrls[req.URL.Path]; ok {
			http.Redirect(respwriter, req, realpath, http.StatusFound)
		} else {
			fallback.ServeHTTP(respwriter, req)
		}
	}
}

// A struct as a go-between for Unmarshal and maps.
type myStruct struct {
	Path string `yaml:"path"`
	URL  string `yaml:"url"`
}

// Wrapper (terminology?) for yaml.Unmarshal and json.Unmarshal
type unmarshalfunc func(in []byte, out interface{}) (err error)

func YAMLHandler(yml []byte, fallback http.Handler) (http.HandlerFunc, error) {
	log.Println("Parsing YAML...")
	return abstractHandler(yml, fallback, yaml.Unmarshal)
}

func JSONHandler(jsn []byte, fallback http.Handler) (http.HandlerFunc, error) {
	log.Println("Parsing JSON...")
	return abstractHandler(jsn, fallback, json.Unmarshal)
}

// Unmarshals the given data using the given unmarshal function
// then converts into a map and uses the maphandler.
func abstractHandler(hierarchy []byte, fallback http.Handler, unmarshal unmarshalfunc) (http.HandlerFunc, error) {
	log.Println("Unmarshalling the data")
	unmarshalList := []myStruct{}
	err := unmarshal(hierarchy, &unmarshalList)
	if err != nil {
		return nil, err
	}

	log.Println("Converting from a list of structs into a map")
	mymap, err := structtomap(unmarshalList)
	if err != nil {
		return nil, err
	}
	return MapHandler(mymap, fallback), nil
}

func structtomap(mylist []myStruct) (map[string]string, error) {
	retmap := make(map[string]string)
	for _, val := range mylist {
		log.Printf("Mapping %s to %s\n", val.Path, val.URL)
		retmap[val.Path] = val.URL
	}
	return retmap, nil
}
