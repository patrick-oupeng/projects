package main

import (
	"fmt"
	"urlshortener"
)

func main() {
	fmt.Println("Main package - not doing anything")
	urlshortener.ExportedMethod()
}
