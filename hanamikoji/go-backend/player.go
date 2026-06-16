package main

import (
	"encoding/json"
	"fmt"
)

type Player struct {
	playerPosition PlayerPosition
	currentPoints  int
	currentGeishas int
	actions        map[ActionName]bool // true for 'taken' false for 'not taken'
	cards          []Suit
	savedCard      Suit
	thrownCards    []Suit
	agent          Agent
}

type PlayerPosition int

const (
	Player1Position PlayerPosition = 0
	Player2Position PlayerPosition = 1
)

func (p *Player) chooseAction(obs Observation) (ActionName, error) {
	validActions := []ActionName{}
	for name, taken := range p.actions {
		if !taken {
			validActions = append(validActions, name)
		}
	}
	if len(validActions) == 0 {
		return "", fmt.Errorf("no available actions")
	}
	return p.agent.ChooseAction(obs, validActions)
}

func (p *Player) chooseCards(obs Observation, nCardsToChoose int) ([]Suit, error) {
	cards, err := p.agent.ChooseCards(obs, nCardsToChoose)
	if err != nil {
		return nil, err
	}
	if len(cards) != nCardsToChoose {
		return nil, fmt.Errorf("wrong number of cards: got %d, want %d", len(cards), nCardsToChoose)
	}
	return cards, nil
}

func (p *Player) makeChoice(obs Observation) (int, error) {
	return p.agent.Respond(obs)
}

// CLI response parsers — used by CLIAgent (not yet implemented)
func parseOutputActionName(output string) (ActionName, error) {
	var s string
	if err := json.Unmarshal([]byte(output), &s); err != nil {
		return "", err
	}
	return ActionName(s), nil
}

func parseOutputCards(output string) ([]Suit, error) {
	var words []string
	if err := json.Unmarshal([]byte(output), &words); err != nil {
		return nil, err
	}
	var foundSuits []Suit
	for _, w := range words {
		s, err := getSuitFromString(w)
		if err != nil {
			return nil, err
		}
		foundSuits = append(foundSuits, s)
	}
	return foundSuits, nil
}

func parseOutputOpponentChoice(output string) (int, error) {
	var choice int
	if err := json.Unmarshal([]byte(output), &choice); err != nil {
		return 0, err
	}
	return choice, nil
}

// ########################
// #    Helper functions  #
// ########################
func (p *Player) resetForNextRound(deck *Deck) error {
	cards, err := deck.DrawCards(starting_cards)
	if err != nil {
		return fmt.Errorf("Failed to draw cards for player %d: %v", p.playerPosition, err)
	}
	p.cards = cards
	p.savedCard = ""
	p.thrownCards = []Suit{}
	for action := range p.actions {
		p.actions[action] = false
	}
	return nil
}

func (p *Player) discard(toDiscard []Suit) error {
	safetyCtr := 0
	for len(toDiscard) > 0 {
		selection := toDiscard[0]
		toDiscard = toDiscard[1:]
		for i, card := range p.cards {
			if selection == card {
				p.thrownCards = append(p.thrownCards, card)
				p.cards = append(p.cards[:i], p.cards[i+1:]...)
				break
			}
		}
		safetyCtr++
		if safetyCtr > 10 {
			return fmt.Errorf("uh-oh, infinite loop in discard?")
		}
	}
	return nil
}

func (p *Player) removeFromHand(cards []Suit) {
	for _, card := range cards {
		for i, c := range p.cards {
			if c == card {
				p.cards = append(p.cards[:i], p.cards[i+1:]...)
				break
			}
		}
	}
}

func (p *Player) save(toSave Suit) error {
	p.savedCard = toSave
	for i, card := range p.cards {
		if toSave == card {
			p.cards = append(p.cards[:i], p.cards[i+1:]...)
			return nil
		}
	}
	return nil
}
