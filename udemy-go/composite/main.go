package main

import (
	"fmt"
	"math/rand"
	"slices"
	"udemy-go/mymodules"
)

// init() runs before main
func init() {
	fmt.Println("This will execute before main")
}

func main() {
	_ = mymodules.KmInMile // just making sure I import right
	forRange()
	fmt.Println("----------")
	slicesAndArrays()
	fmt.Println("----------")
	testMaps()
	fmt.Println("----------")
	testslice := make([]int, 5)
	fmt.Println("Before manipulation", testslice)
	manipulate(testslice)
	fmt.Println("After manipulation", testslice)
	fmt.Println("----------")
	structs()
	fmt.Println("----------")
	unfurlSlice := []int{1, 2, 3, 4}
	fmt.Println("My sum:", variadicsum(unfurlSlice...)) // the ... passes each value separately
	// fmt.Println(unfurlSlice...) // errors
	fmt.Println("----------")
	pointers()
}

func manipulate(inputslice []int) {
	// inputslice points to the same underlying array
	// changing the values affects the original object
	inputslice[0] = 7
	inputslice[4] = 2
	// technically doing clever stuff with append() is better than Delete but idc
	inputslice = slices.Delete(inputslice, 2, 3) // deletes indices a:b from input

	// changing the length / capacity of inputslice does not affect the original object
	// There's probably some interaction where we pre-populate values if we try to expand the original
	inputslice = append(inputslice, inputslice...)
	fmt.Println("Our inputslice", inputslice)
}

func forRange() {
	// testing slices and ranges
	somenumber := rand.Intn(100) + 1
	fmt.Println("\nRange time")
	// stupid loop but show me range
	for index := range somenumber {
		// statement idiom:
		// this is how you do if(myFunction() == somenumber)
		if z := rand.Intn(100) + 1; z == somenumber {
			fmt.Printf("Found it! number is %d, index %d\n", somenumber, index)
			break
		}
	}
}

func slicesAndArrays() {
	fmt.Println("Array time")
	// somearray := [...]int{} // totally empty, no size
	// somearray := [...]int{3,3,3,3} // auto-detect size
	var somearray [3]int // empty, size 3
	somearray[0] = 3
	somearray[2] = 81
	// somearray = append(somearray[:], 2) // errors, somearray is strictly typed with length 3
	fmt.Println(somearray)
	fmt.Println("length", len(somearray))
	// somearray[3] = 1000 // error out of bounds

	fmt.Println("\nSlice time")
	// 'make' used to initialize empty complex types
	// make(type, initial length, capacity)
	// capacity is useful if I know roughly how many elements it should have, but not strict. It defines the starting underlying array
	someslice := make([]int, 0, 3)
	fmt.Println("Make syntax:", someslice, len(someslice), cap(someslice))
	// empty length initializer lets it be dynamically sized
	someslice = []int{1, 2, 420, 69, 31}
	fmt.Println("size increase:", someslice, len(someslice), cap(someslice))
	// someslice = append(someslice[2:4], 3) // indices are [a, b) so this will be [420, 69] and then append 3
	someslice = append(someslice[:2], someslice[3:]...) // can pass slices and arrays into append
	refslice := someslice                               // references the same underlying array
	copyslice := make([]int, len(someslice))
	copy(copyslice, someslice) // copies b into a
	someslice[0] = 4
	fmt.Println("orig", someslice, "| reference", refslice, "| copy", copyslice)
}

func testMaps() {
	fmt.Println("Map time")
	somemap := map[int]string{
		31:  "Age",
		185: "Height",
		60:  "Weight",
	}
	somemap[101] = "Taipei" // new element
	delete(somemap, 185)
	for k, v := range somemap { // unordered
		fmt.Println(k, v)
	}

	// so i guess everything returns a value and an error in Go?
	key := 100
	if val, ok := somemap[key]; ok {
		fmt.Printf("Value %s is in map\n", val)
		fmt.Printf("ok: %t %v\n", ok, ok)
	} else {
		fmt.Printf("key %d is not in map\n", key)
		fmt.Printf("ok: %T %v\n", ok, ok)
	}
}

type person struct {
	first string
	last  string
	age   int
}
type engineer struct {
	person   // can also be defined anonymously
	employed bool
	language string
}

func (p person) greeting() { // method for person struct
	fmt.Println("My name is ", p.first, p.last)
}

func (e engineer) greeting() { // method for person struct
	fmt.Println("My name is ", e.first, e.last)
	if !e.employed {
		fmt.Println("I use the coding language ", e.language)
	}
}

// If any type has the 'greeting' method, then it's also of the 'human' type
// This is useful to have a function that takes in type: human and calls the greeting() method
type human interface {
	greeting()
}

func sayHi(h human) {
	h.greeting()
}

func structs() {
	fmt.Println("Struct time")

	me := person{
		first: "John",
	}
	me.greeting()
	anonymous := struct {
		first string
		last  string
		age   int
	}{
		first: "James",
		last:  "Bond",
	}

	resume := engineer{
		person:   me, // is a copy
		employed: true,
		language: "python",
	}

	// using the 'human' interface
	sayHi(resume)
	sayHi(me)

	directory := map[int]person{
		1720: me,
		1009: anonymous, // same fields, so it accepts it
	}

	me.age = 5
	fmt.Println("Me: ", me)
	fmt.Println("Accessing each field:", me.first, me.last)
	fmt.Println("My resume: ", resume)
	fmt.Println("Resume firstname: ", resume.first) // sub-struct fields are promoted
	fmt.Println("Anonymous: ", anonymous)
	fmt.Printf("type of me: %T\n", me)
	fmt.Printf("type of anon: %T\n", anonymous)
	fmt.Println("Directory: ", directory)
}

func variadicsum(inputs ...int) int {
	fmt.Printf("Inputs are %v of type %T\n", inputs, inputs)
	var result int
	for _, val := range inputs {
		result += val
	}
	return result
}

func pointers() {
	fmt.Println("Pointer time")
	somevariable := 42
	somepointer := &somevariable
	fmt.Printf("Var is %v | pointer addr is %v | dereferenced pointer is %v | pointer to pointer is %v\n", somevariable, somepointer, *somepointer, &somepointer)
}
