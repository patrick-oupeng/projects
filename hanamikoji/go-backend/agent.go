package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
)

type Agent interface {
	ChooseAction(obs Observation, validActions []ActionName) (ActionName, error)
	ChooseCards(obs Observation, n int) ([]Suit, error)
	Respond(obs Observation) (int, error)
}

type RandomAgent struct{}

func (r *RandomAgent) ChooseAction(_ Observation, valid []ActionName) (ActionName, error) {
	return valid[rand.Intn(len(valid))], nil
}

func (r *RandomAgent) ChooseCards(obs Observation, n int) ([]Suit, error) {
	hand := append([]Suit{}, obs.MyHand...)
	rand.Shuffle(len(hand), func(i, j int) { hand[i], hand[j] = hand[j], hand[i] })
	return hand[:n], nil
}

func (r *RandomAgent) Respond(obs Observation) (int, error) {
	if len(obs.OfferedGift) > 0 {
		return rand.Intn(len(obs.OfferedGift)), nil
	}
	return rand.Intn(2), nil
}

// CLIAgent serialises StepRequests to stdout and reads JSON decisions from stdin.
// Create one instance and share it across both players — decisions are sequential.
type CLIAgent struct {
	scanner *bufio.Scanner
}

func NewCLIAgent() *CLIAgent {
	s := bufio.NewScanner(os.Stdin)
	s.Buffer(make([]byte, 1<<20), 1<<20) // 1 MB — more than enough for any observation
	return &CLIAgent{scanner: s}
}

func (c *CLIAgent) writeReq(req StepRequest) error {
	data, err := json.Marshal(req)
	if err != nil {
		return err
	}
	_, err = fmt.Fprintln(os.Stdout, string(data))
	return err
}

func (c *CLIAgent) readLine() ([]byte, error) {
	if !c.scanner.Scan() {
		if err := c.scanner.Err(); err != nil {
			return nil, err
		}
		return nil, fmt.Errorf("stdin closed")
	}
	b := make([]byte, len(c.scanner.Bytes()))
	copy(b, c.scanner.Bytes())
	return b, nil
}

func (c *CLIAgent) ChooseAction(obs Observation, validActions []ActionName) (ActionName, error) {
	if err := c.writeReq(StepRequest{Step: ChooseActionStep, Observation: obs, ValidActions: validActions}); err != nil {
		return "", err
	}
	line, err := c.readLine()
	if err != nil {
		return "", err
	}
	var action ActionName
	return action, json.Unmarshal(line, &action)
}

func (c *CLIAgent) ChooseCards(obs Observation, n int) ([]Suit, error) {
	if err := c.writeReq(StepRequest{Step: ChooseCardsStep, Observation: obs, NCardsToChoose: n}); err != nil {
		return nil, err
	}
	line, err := c.readLine()
	if err != nil {
		return nil, err
	}
	var cards []Suit
	return cards, json.Unmarshal(line, &cards)
}

func (c *CLIAgent) Respond(obs Observation) (int, error) {
	if err := c.writeReq(StepRequest{Step: OpponentResponseStep, Observation: obs}); err != nil {
		return 0, err
	}
	line, err := c.readLine()
	if err != nil {
		return 0, err
	}
	var choice int
	return choice, json.Unmarshal(line, &choice)
}
