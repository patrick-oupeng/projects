package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"strings"
	"time"
)

const DEFAULT_FILENAME = "problems.csv" // question,answer
const DEFAULT_TIME = 30                 // seconds
const DEFAULT_LOGFILE = "logfile.txt"

var csvname string
var logname string
var timelimit int64
var numquestions int
var numright int

// Init parses the command line arguments and sets the relevant variables.
func init() {
	log.SetPrefix("Quiz ")
	csvname = DEFAULT_FILENAME
	logname = DEFAULT_LOGFILE
	timelimit = DEFAULT_TIME
	args := os.Args[1:] // first val is program
	// only set variables, don't open anything. Because defer close should happen in main
	if len(args) > 0 {
		for index, val := range args {
			// I probably should have a check if the user passes a flag but no input after
			if (val == "--csv" || val == "-c") && index+1 < len(args) {
				csvname = args[index+1]
			} else if (val == "--limit" || val == "-t") && index+1 < len(args) {
				timelimit, _ = strconv.ParseInt(args[index+1], 10, 64)
				if timelimit < 1 {
					log.Println("Passed in too low of a time limit; using default")
					timelimit = DEFAULT_TIME
				}
			} else if (val == "--logfile" || val == "-l") && index+1 < len(args) {
				logname = args[index+1]
			}
		}
	}
}

// Main is the main function.
func main() {
	// set log file stuff
	log.Println("Setting log file to", logname)
	logfile, err := os.Create(logname)
	if err != nil {
		log.Fatalln(err) // logfile hasn't been set so this will print to stdout
	}
	mw := io.MultiWriter(os.Stdout, logfile) // write to both stdout and logfile
	defer logfile.Close()
	log.SetOutput(mw)

	// open csv file
	log.Println("Opening csv file:", csvname)
	csvfile, err := os.Open(csvname)
	if err != nil {
		log.Fatalln(err)
	}
	defer csvfile.Close()

	// parse the csv into rows
	log.Println("Attempting to parse CSV...")
	csv_reader := csv.NewReader(csvfile)
	records, err := csv_reader.ReadAll()
	if err != nil {
		log.Fatal("Unable to parse CSV ", csvname, err)
	}
	numquestions = len(records)
	log.Printf("Got %d records", numquestions)
	// actually run the quiz
	timeup := make(chan bool)
	endquiz := make(chan bool)

	// I could put this inside the quiz start, but then I have to kick off the timer there as well.
	fmt.Println("Beginning quiz. After each question type your answer and then enter.")
	fmt.Println("You have", timelimit, "seconds to complete the quiz.")
	fmt.Println("Press enter to begin.")
	bufio.NewReader(os.Stdin).ReadString('\n') // wait for a new line
	go runquiz(records, endquiz)
	go starttimer(timeup)

	select {
	case <-timeup:
		fmt.Println("\nTime's up!")
	case <-endquiz:
		fmt.Println("\nCongratulations, you finished the quiz!")
	}
	fmt.Printf("Correctly answered %d/%d questions\n", numright, numquestions)
}

func starttimer(signalchan chan<- bool) {
	time.Sleep(time.Duration(timelimit) * time.Second)
	signalchan <- true
}

// Runs the main quiz.
func runquiz(csvrows [][]string, signalchan chan<- bool) {
	var userinput string
	var inputint int
	reader := bufio.NewReader(os.Stdin)
	prefix_string := "0"
	for rownum, row := range csvrows {
		if rownum+1 > 9 {
			prefix_string = ""
		}
		problem := row[0]
		soln, err := strconv.Atoi(strings.TrimSpace(row[1]))
		if err != nil {
			log.Panic("Non-numeric solution in the row! Row", rownum, "has value", soln)
		}
		for {
			fmt.Printf("%s%d/%d | %s : ", prefix_string, rownum+1, numquestions, problem)
			userinput, err = reader.ReadString('\n')
			// _, err := fmt.Scanln(&input) // this errors with multiple inputs
			if err != nil || len(strings.Fields(userinput)) != 1 {
				log.Println("Error scanning input; try again")
				continue
			} else {
				inputint, err = strconv.Atoi(strings.TrimSpace(userinput))
				if err != nil {
					log.Printf("User input '%s' is not a valid int; try again", userinput)
					continue
				}
			}
			break
		}
		if inputint == soln {
			numright++
			fmt.Println("Correct!")
		} else {
			fmt.Println("WRONG YOU IDIOT")
		}
	}
	signalchan <- true
}
