package main

import (
	"fmt"
	"math/rand/v2"
)

type Deck []Suit

type Suit string

const (
	Flute    Suit = "Flute"
	Fan      Suit = "Fan"
	Scroll   Suit = "Scroll"
	Parasol  Suit = "Parasol"
	Shamisen Suit = "Shamisen"
	TeaSet   Suit = "TeaSet"
	HairPin  Suit = "HairPin"
)

func getSuitFromString(word string) (Suit, error) {
	switch word {
	case string(Flute):
		return Flute, nil
	case string(Fan):
		return Fan, nil
	case string(Scroll):
		return Scroll, nil
	case string(Parasol):
		return Parasol, nil
	case string(Shamisen):
		return Shamisen, nil
	case string(TeaSet):
		return TeaSet, nil
	case string(HairPin):
		return HairPin, nil
	default:
		return "", fmt.Errorf("unable to parse suit")
	}
}

type markerPosition int

const (
	startingMarkerPosition markerPosition = 0
	Player1                markerPosition = 1
	Player2                markerPosition = 2
)

type Geisha struct {
	Suit           Suit
	Points         int
	Player1Cards   int
	Player2Cards   int
	MarkerPosition markerPosition
}

var Ayane = &Geisha{
	Suit:           Flute,
	Points:         2,
	MarkerPosition: startingMarkerPosition,
}

var Iroha = &Geisha{
	Suit:           Fan,
	Points:         2,
	MarkerPosition: startingMarkerPosition,
}

var Tomoyo = &Geisha{
	Suit:           Scroll,
	Points:         2,
	MarkerPosition: startingMarkerPosition,
}

var Chiharu = &Geisha{
	Suit:           Parasol,
	Points:         3,
	MarkerPosition: startingMarkerPosition,
}

var Yoko = &Geisha{
	Suit:           Shamisen,
	Points:         3,
	MarkerPosition: startingMarkerPosition,
}

var Anju = &Geisha{
	Suit:           TeaSet,
	Points:         4,
	MarkerPosition: startingMarkerPosition,
}

var Ruri = &Geisha{
	Suit:           HairPin,
	Points:         5,
	MarkerPosition: startingMarkerPosition,
}

func makeDeck() Deck {
	return Deck{
		Flute, Flute,
		Fan, Fan,
		Scroll, Scroll, Scroll,
		Parasol, Parasol, Parasol,
		Shamisen, Shamisen, Shamisen,
		TeaSet, TeaSet, TeaSet, TeaSet,
		HairPin, HairPin, HairPin, HairPin, HairPin,
	}
}

func shuffleDeck(oldDeck Deck) Deck {
	newDeck := make(Deck, len(oldDeck))
	perm := rand.Perm(len(oldDeck))
	for i, v := range perm {
		newDeck[i] = oldDeck[v]
	}
	return newDeck
}

func (d *Deck) DrawCards(toDraw int) ([]Suit, error) {
	if len(*d) == 0 {
		return nil, fmt.Errorf("Deck is empty")
	}
	cards := (*d)[:toDraw]
	*d = (*d)[toDraw:]
	return cards, nil
}

func (d *Deck) DrawOne() (Suit, error) {
	drawn, err := d.DrawCards(1)
	if err != nil {
		return "", err
	}
	return drawn[0], nil
}

func makePlayingField() []*Geisha {
	return []*Geisha{Ayane, Iroha, Tomoyo, Chiharu, Yoko, Anju, Ruri}
}
