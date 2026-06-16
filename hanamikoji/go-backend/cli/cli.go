package cli

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

type CLI struct {
	reader *bufio.Reader
}

func New() *CLI {
	return &CLI{reader: bufio.NewReader(os.Stdin)}
}

func (c *CLI) GetResponse(jsonData []byte) (string, error) {
	fmt.Println(string(jsonData))
	line, err := c.reader.ReadString('\n')
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(line), nil
}
