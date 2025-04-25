package main

import (
	"fmt"
	"math/rand"
)

// This does not work outside of a function
// everything has to start with a keyword
// p := 2

// Go uses conversion, not casting
// i = 42
// j = float(i)

func main() {
	fmt.Println("hello")
	const a = "testing my variables!"
	const b = 0b111110 // binary prefix; untyped constant - context-based type
	c := 5             // quick initialization
	var d int          // initialize to zero / false / nil
	d = 20             // later assignment
	var e int = 17     // verbose assignment
	e = e + 2
	e += 2
	f := add(d, e)
	var i, j, k, l = 1, 2.0, true, "no"
	fmt.Println(i, j, k, l)
	var ( // block var declaration
		outside int = -42
		inside  int = 69
	)
	faren, cel := tofarenheit(outside)
	fmt.Printf("%d in Farenheit is %d in Celsius\n", faren, cel)
	faren, cel = tofarenheit(inside)
	fmt.Printf("%d in Farenheit is %d in Celsius\n", faren, cel)
	fmt.Printf("Sum of %d and %d: %d\n", d, e, f)
	fmt.Printf("%s %d type %T\n", a, b, b)
	fmt.Printf("Decimal: %d, %d | Binary: %b, %b | Hex: %x, %x\n", b, c, b, c, b, c)
	fmt.Printf("Unicode character represented by hex %x: %c\n", b, b)
	printxtimes(2, "testing")
	fib(0, 0)
	switching()
	switching()
	switching()
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
	defer fmt.Printf("The initial values for the starting int and the limit are %d and %d\n", initial, limit)
	defer fmt.Println("\nThis will be printed before the above. Defers stack, not list")
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
