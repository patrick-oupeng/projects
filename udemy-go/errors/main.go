package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"time"
)

// in this file, I am testing error checking and logging
func main() {
	filename := "Log.txt"
	f, err := os.Create(filename)
	if err != nil {
		log.Fatalln(err)
	}
	log.SetFlags(log.LstdFlags | log.Lshortfile) // add filename to logging
	log.SetPrefix("My own prefix ")
	fmt.Println("Check logging file:", f.Name()) // or filename | not sure if you can do like `log.filename`
	log.SetOutput(f)
	defer f.Close()
	log.Println("This doesn't do anything yet!")
	_, err = myAddition(-1, -1)
	if err != nil {
		log.Println("Got an error in MyAddition:", err)
	}
	_, err = myAddition(5, 5)
	if err != nil {
		log.Println("Got an error in MyAddition:", err)
	}

	testPanic()
}

type myError struct {
	name   string
	number int
	err    error
}

// by implementing the Error() function, my struct implicitly becomes of type error interface
// This allow lots of flexibility to add more information
func (m myError) Error() string {
	return fmt.Sprintf("a myError occurred: name %v number %v error %v", m.name, m.number, m.err)
}

func myAddition(n1, n2 int) (mysum int, err error) {
	time.Sleep(10 * time.Microsecond)
	if n1 < 0 && n2 < 0 {
		// fmt.Errorf also does errors.New
		return 0, errors.New("cannot add two negative numbers, don't ask why")
	}
	if n1 == 5 && n2 == 5 {
		err = errors.New("what happened?")
		return 0, myError{"TooManyFives", 2, err}
	}
	return n1 + n2, nil
}

func testPanic() {
	log.Println("Will panic")
	defer log.Println("Deferred line")
	log.Panic("Panicking!! AAAAHHH!!!!")
}
