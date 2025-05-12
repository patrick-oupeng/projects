// This is the primary file for completing gophercises exercise 2.
// Original stub file downloaded from:
// https://github.com/gophercises/urlshort/blob/master/handler.go
package urlshortener

import (
	"net/http"

	"github.com/go-yaml/yaml"
)

// MapHandler will return an http.HandlerFunc (which also
// implements http.Handler) that will attempt to map any
// paths (keys in the map) to their corresponding URL (values
// that each key in the map points to, in string format).
// If the path is not provided in the map, then the fallback
// http.Handler will be called instead.
func MapHandler(pathsToUrls map[string]string, fallback http.Handler) http.HandlerFunc {
	return func(respwriter http.ResponseWriter, req *http.Request) {
		if realpath, ok := pathsToUrls[req.URL.Path]; ok {
			http.Redirect(respwriter, req, realpath, http.StatusFound)
		} else {
			fallback.ServeHTTP(respwriter, req)
		}
	}
}

// YAMLHandler will parse the provided YAML and then return
// an http.HandlerFunc (which also implements http.Handler)
// that will attempt to map any paths to their corresponding
// URL. If the path is not provided in the YAML, then the
// fallback http.Handler will be called instead.
//
// YAML is expected to be in the format:
//
//   - path: /some-path
//     url: https://www.some-url.com/demo
//
// The only errors that can be returned all related to having
// invalid YAML data.
//
// See MapHandler to create a similar http.HandlerFunc via
// a mapping of paths to urls.
type myYaml struct {
	Path string `yaml:"path"`
	URL  string `yaml:"url"`
}

func YAMLHandler(yml []byte, fallback http.Handler) (http.HandlerFunc, error) {
	yamlList := []myYaml{}
	err := yaml.Unmarshal(yml, &yamlList)
	if err != nil {
		return nil, err
	}

	mymap, err := yamltomap(yamlList)
	if err != nil {
		return nil, err
	}
	return MapHandler(mymap, fallback), nil
}

func yamltomap(mylist []myYaml) (map[string]string, error) {
	retmap := make(map[string]string)
	for _, val := range mylist {
		retmap[val.Path] = val.URL
	}
	return retmap, nil
}
