package main

import "fmt"

// TODO fill in the actual actions

type Action struct {
	actionName               ActionName
	nCardsToChoose           int
	requiresOpponentResponse bool
}

var Secret Action = Action{
	actionName:               SecretName,
	nCardsToChoose:           1,
	requiresOpponentResponse: false,
}

var Discard Action = Action{
	actionName:               DiscardName,
	nCardsToChoose:           2,
	requiresOpponentResponse: false,
}

var Gift Action = Action{
	actionName:               GiftName,
	nCardsToChoose:           3,
	requiresOpponentResponse: true,
}

var Competition Action = Action{
	actionName:               CompetitionName,
	nCardsToChoose:           4,
	requiresOpponentResponse: true,
}

type ActionName string

const (
	SecretName      ActionName = "Secret"
	DiscardName     ActionName = "Discard"
	GiftName        ActionName = "Gift"
	CompetitionName ActionName = "Competition"
)

func getActionFromString(name string) (Action, error) {
	switch name {
	case string(SecretName):
		return Secret, nil
	case string(DiscardName):
		return Discard, nil
	case string(GiftName):
		return Gift, nil
	case string(CompetitionName):
		return Competition, nil
	default:
		return Action{}, fmt.Errorf("Invalid action name: %s", name)
	}
}

func getActionFromName(name ActionName) (Action, error) {
	switch name {
	case SecretName:
		return Secret, nil
	case DiscardName:
		return Discard, nil
	case GiftName:
		return Gift, nil
	case CompetitionName:
		return Competition, nil
	default:
		return Action{}, fmt.Errorf("Invalid action name: %s", name)
	}
}

func defaultActions() map[ActionName]bool {
	return map[ActionName]bool{
		SecretName:      false,
		DiscardName:     false,
		GiftName:        false,
		CompetitionName: false,
	}
}
