package mymodules

/*
* to get importing to work:
* 1. go mod init udemy-go (the directory that main.go is in)
* 2. create mymodules dir and any files within
* 3. main.go: import "udemy-go/mymodules"
* Note: I am not sure why it does not use mymodules.speed.Light.
* Probably I would need sub-modules.
 */
const Light = 3.2
const Gravity = 9.8
const KmInMile = 1.6

var Car = 69
