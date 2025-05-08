package main

import (
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	fmt.Println("CPU", runtime.NumCPU())
	fmt.Println("Routines", runtime.NumGoroutine())
	// fmt.Println("This doesn't do anythign yet.")
	fmt.Println("===================")
	basicThread()
	usemutex := true
	fmt.Println("===================")
	raceCondition(!usemutex)
	fmt.Println("===================")
	raceCondition(usemutex)
	fmt.Println("===================")
	atomicRace()
	fmt.Println("===================")
	channelError()
	channelBuffer()
	channelCorrect()
	channelTypes()
	channelRange()
	fmt.Println("===================")
	selectChannel()
}

func selectChannel() {
	// var wg sync.WaitGroup
	ch1 := make(chan int)
	ch2 := make(chan int)
	stopchan := make(chan bool)
	// wg.Add(1)
	go sendToChan(ch1, ch2, stopchan, 100)
	for {
		select {
		case v, ok := <-ch1:
			if ok {
				fmt.Println("Multiple of five:", v)
			}
		case v, ok := <-ch2:
			if ok {
				fmt.Println("Multiple of seven:", v)
			}
		case v := <-stopchan:
			fmt.Println("Got signal to stop. Returning", v)
			return
		}
	}
}

// sends multiples of 5 to one chanenl and multiples of 7 to another
func sendToChan(fives, sevens chan<- int, quit chan<- bool, limit int) {
	for i := range limit {
		if i == 0 {
			continue
		}
		if i%5 == 0 {
			fives <- i
		}
		if i%7 == 0 {
			sevens <- i
		}
		if i%35 == 0 {
			// having the close() causes the select to see 0s
			// if using close, we should use 'ok' idiom
			// I don't really need to close with select
			close(fives)
			close(sevens)
			quit <- true
			break // stop looping
		}
	}
}

func channelRange() {
	ch := make(chan int)
	go func() {
		for i := range 100 {
			ch <- i
		}
		close(ch) // needed, otherwise `range ch` never exits
	}()

	// for range ch { // also works
	for v := range ch { // continues until there are no values on the channel
		if v == 99 {
			fmt.Println("Range over channel - Done iterating on ch")
		}
	}
}

// testing receive-only and send-only channels
func channelTypes() {
	ch := make(chan int)
	go sendValue(ch)
	receiveValue(ch) // no 'go' so it's blocking
}

// pass in a send-only channel
func sendValue(ch chan<- int) {
	// a := <-ch // errors!
	ch <- 45
}

// pass in a receive-only channel
func receiveValue(ch <-chan int) {
	// ch <- 25 // errors!
	fmt.Println("Received value from the receive-only channel:", <-ch)
}

func channelCorrect() {
	ch := make(chan int)
	go func() { // this launches and waits until a receiver is ready
		ch <- 50
	}()
	fmt.Println("Using channel with thread - Got a value from the channel:", <-ch)
}

// same as error but with a buffer size 1 so it works
// don't over-rely on buffers
func channelBuffer() {
	ch := make(chan int, 1)
	ch <- 5
	fmt.Println("Using channel with buffer - Got a value from the channel:", <-ch)
}

// this will error!
func channelError() {
	return
	ch := make(chan int)
	ch <- 5 // this blocks permanently since there isn't a receiver ready
	fmt.Println(<-ch)
}

// do the same thing as racecondition
// but use atomic
func atomicRace() {
	fmt.Println("Using atomic package to index counter")

	const limit = 10000
	var wg sync.WaitGroup
	wg.Add(limit) // 'we will be launching this many threads'
	var counter uint64
	maxRoutines := 0

	for range limit {
		go func() {
			atomic.AddUint64(&counter, 1)
			wg.Done() // 'this thread is done'
		}()
		if runtime.NumGoroutine() > maxRoutines {
			maxRoutines = runtime.NumGoroutine()
		}
	}
	wg.Wait() // 'wait until all the threads say they're done'. blocks execution of next line
	fmt.Println("Max number of goroutines was", maxRoutines)
	if atomic.LoadUint64(&counter) != limit {
		fmt.Println("Error! Expected count", limit, "but got count", atomic.LoadUint64(&counter))
	} else {
		fmt.Println("Counter is working as intended; no race conditions here :)")
	}
}

func raceCondition(shouldLock bool) {
	if shouldLock {
		fmt.Println("Testing race condition with locking")
	} else {
		fmt.Println("Testing race condition without locking")
	}
	const limit = 10000
	var wg sync.WaitGroup
	wg.Add(limit) // 'we will be launching this many threads'
	var locker sync.Mutex
	counter := 0
	maxRoutines := 0

	for range limit {
		go func() {
			if shouldLock {
				// mutex locks anything accessing the lines of code until the unlock
				locker.Lock()
				defer locker.Unlock()
			}
			tempvar := counter
			tempvar += 1
			counter = tempvar
			wg.Done() // 'this thread is done'
		}()
		if runtime.NumGoroutine() > maxRoutines {
			maxRoutines = runtime.NumGoroutine()
		}
	}
	wg.Wait() // 'wait until all the threads say they're done'. blocks execution of next line
	fmt.Println("Max number of goroutines was", maxRoutines)
	if counter != limit {
		fmt.Println("Error! Expected count", limit, "but got count", counter)
	} else {
		fmt.Println("Counter is working as intended; no race conditions here :)")
	}
}

func basicThread() {
	ch := make(chan int)
	// fmt.Println(<-ch)
	go func() { // anonymous function to wrap my adding
		ch <- addOne(4)
	}()
	fmt.Println("Testing threading:", <-ch) // this automatically waits
}

func addOne(i int) int {
	time.Sleep(100 * time.Millisecond)
	return i + 1
}
