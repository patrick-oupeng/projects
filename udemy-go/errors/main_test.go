package main

import (
	"testing"
)

// shows how to run a test.
// func name `Test<funcname>` isn't required but best practice
func TestMyAddition(t *testing.T) {
	// vscode tells me this is redundant because it could just be a []int
	type totest struct {
		data     []int
		expected int
	}
	testlist := []totest{
		totest{[]int{1, 1}, 2},
		totest{[]int{2, 2}, 4},
		totest{[]int{10, 9}, 19},
		// totest{[]int{20, 20}, 1},
	}

	for _, v := range testlist {
		actual, _ := myAddition(v.data[0], v.data[1])
		if actual != v.expected {
			t.Error("Expected", v.expected, "Got", actual)
		}
	}
}

// Naming something 'Example<funcname>' will automatically export it
// as an example in the documentation.
func ExamplemyAddition() {
	_, _ = myAddition(100, 1)
	// Output:
	// 2
}

// This allows us to run 'go test bench <dir or funcname>' to get a timing benchmark
func BenchmarkMyAddition(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_, _ = myAddition(100, 1)
	}
}
