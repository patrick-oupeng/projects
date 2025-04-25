package main

import "fmt"

func main() {
	fmt.Println("hello")
	const a = "testing my variables!"
	const b = 0b111110
	c := 5
	fmt.Printf("%s %d type %T\n", a, b, b)
	fmt.Printf("Decimal: %d, %d | Binary: %b, %b | Hex: %x, %x\n", b, c, b, c, b, c)
	fmt.Printf("Unicode character represented by hex %x: %c\n", b, b)
}
