package main

import "math/rand"

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
