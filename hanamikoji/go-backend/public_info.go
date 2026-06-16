package main

// Used to store public information for a given player. Passed inside StepRequest for ML stuff.
type Observation struct {
	PlayingField     []*Geisha
	MyActions        map[ActionName]bool
	OpponentActions  map[ActionName]bool
	MySavedCard      Suit
	MyDiscardedCards []Suit
	MyHand           []Suit

	// set when the opponent must respond to an action
	OfferedGift        []Suit
	OfferedCompetition []Suit
}

// JSON passed to cli for python ML to read
type StepRequest struct {
	Step           StepState    `json:"step"`
	Observation    Observation  `json:"observation"`
	ValidActions   []ActionName `json:"valid_actions,omitempty"`
	NCardsToChoose int          `json:"n_cards_to_choose,omitempty"`
}

type StepState string

const (
	ChooseActionStep     StepState = "ChooseAction"
	ChooseCardsStep      StepState = "ChooseCards"
	OpponentResponseStep StepState = "OpponentResponse"
)

// Used to track the game state during an action
type PendingAction struct {
	action            Action
	activePlayer      PlayerPosition
	chosenSecret      Suit
	chosenDiscard     []Suit
	chosenGift        []Suit // 3 cards
	chosenCompetition []Suit // 4 cards, 0 and 1 are the first group; 2 and 3 are the second
	opponentChoice    int
}
