package main

// This file covers the first ~50 lectures of the Udemy go course
// There is a lot of overlap with the 'tour of go'

import (
	"fmt"
	"math/rand"
	"udemy-go/mymodules"
)

// Assignment does not work outside of a function
// everything has to start with a keyword
// p := 2

// Go uses conversion, not casting
// i = 42
// j = float(i)
// constants are converted dynamically according to context??

func main() {
	//basic variables and printing
	variable_testing()
	var ( // block var declaration
		outside int = -42
		inside  int = 69
	)
	// start writing methods with passed variables and returns
	faren, cel := tofarenheit(outside)
	fmt.Printf("%d in Farenheit is %d in Celsius\n", faren, cel)
	faren, cel = tofarenheit(inside)
	fmt.Printf("%d in Farenheit is %d in Celsius\n", faren, cel)
	// for loop
	printxtimes(2, "testing")
	// while (cond) and defer
	fib(0, 0)
	// switch statement
	switching()
	powersoftwo()
	sizes()
	speed := mymodules.Light
	fmt.Println(speed)
}

const (
	_  = iota
	kb = 1 << (10 * iota) // bytes
	mb
	gb
	tb
	pb
	eb
)

func sizes() {
	fmt.Printf("1 kb is %d bytes | %b \n", kb, kb)
	fmt.Printf("1 mb is %d bytes | %b \n", mb, mb)
	fmt.Printf("1 gb is %d bytes | %b \n", gb, gb)
	fmt.Printf("1 tb is %d bytes | %b \n", tb, tb)
	fmt.Printf("1 pb is %d bytes | %b \n", pb, pb)
	fmt.Printf("1 eb is %d bytes | %b \n", eb, eb)
}

// iota is used when declaring constants
// iterated once per non-blank line
// reset to 0 at a 'const' declaration
const (
	one = 1 << iota
	two
	four
	eight
)

func powersoftwo() {
	fmt.Println(one, two, four, eight)
}

func variable_testing() {
	fmt.Println("hello")
	const a = "testing my variables!"
	const b = 0b111110 // binary prefix; untyped constant - context-based type
	c := 5             // quick initialization
	var d int          // initialize to zero / false / nil
	d = 20             // later assignment
	var e int = 17     // verbose assignment
	e = e + 2
	e += 2
	var i, j, k, l = 1, 2.0, true, "no"
	fmt.Println(i, j, k, l)
	// more vars
	f := add(d, e)
	fmt.Printf("Sum of %d and %d: %d\n", d, e, f)
	// print out var types and stuff
	fmt.Printf("%s %d type %T\n", a, b, b)
	fmt.Printf("Decimal: %d, %d | Binary: %b, %b | Hex: %x, %x\n", b, c, b, c, b, c)
	fmt.Printf("Unicode character represented by hex %x: %c\n", b, b)
}

func add(x, y int) int { // x/y are same types so we only say once
	fmt.Printf("x %d and y %d are both integers\n", x, y)
	return x + y
}

// you can define named returns at the top of the function
// this acts as a declaration of those variables
// then, a 'naked return' just returns those variables
func tofarenheit(input_temp int) (farenheit, celcius int) {
	farenheit = input_temp
	celcius = ((input_temp - 32) * 5) / 9
	return
}

// for loop syntax
func printxtimes(times int, s string) {
	for i := 0; i < times; i++ {
		println(s)
	}
}

// a while(cond) loop is spelled 'for'
// can even do `for {}` if you want infinite, or `for <bool> {}`
func fib(initial, limit int) {
	// defer is cool - waits until the surrounding function returns to execute
	// but evaluates at the time you'd expect
	defer fmt.Printf("Defer 1: The initial values for the starting int and the limit are %d and %d\n", initial, limit)
	defer fmt.Println("\nDefer 2: This will be printed before the above. Defers stack, not list")
	if initial == 0 { // nothing is passed in
		initial = 1
	}
	if limit == 0 {
		limit = 1000
	}
	other_value := initial
	fmt.Println(initial, other_value)
	for initial < limit {
		if initial == 89 || other_value == 89 { // 'if' syntax is how i would expect
			fmt.Print(" nice ")
		}
		initial += other_value
		other_value = initial - other_value
		fmt.Printf(" %d ", initial)
	}
}

func switching() {
	fmt.Print("Today's lucky winner is...")
	lucky := rand.Intn(70)
	switch lucky {
	case 69:
		fmt.Println("Nice")
	case 7:
		fmt.Println("Lucky!")
	case 13:
		fmt.Println("Unlucky!")
	case 1:
		fmt.Println("first place")
	// errors since switch already has a condition
	// case lucky < 25:
	default:
		fmt.Println("Sorry, not today!")
		fmt.Printf("You got: %d\n", lucky)
	}
	switch { // same as `switch true`
	case lucky < 10:
		fmt.Println("Too small")
	case lucky > 50:
		fmt.Println("Too big")
	}

}
