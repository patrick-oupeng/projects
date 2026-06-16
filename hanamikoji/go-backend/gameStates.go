package main

import "fmt"

func (g *Game) StepChooseAction(player *Player, observation Observation) error {
	chosenActionName, err := player.chooseAction(observation)
	if err != nil {
		return err
	}
	action, err := getActionFromName(chosenActionName)
	if err != nil {
		return err
	}
	g.pendingAction = &PendingAction{action: action}
	player.actions[chosenActionName] = true
	return nil
}

func (g *Game) StepChooseCards(player *Player, observation Observation) error {
	chosenCards, err := player.chooseCards(observation, g.pendingAction.action.nCardsToChoose)
	if err != nil {
		return err
	}
	switch g.pendingAction.action.actionName {
	case SecretName:
		g.pendingAction.chosenSecret = chosenCards[0]
	case DiscardName:
		g.pendingAction.chosenDiscard = chosenCards
	case GiftName:
		g.pendingAction.chosenGift = chosenCards
	case CompetitionName:
		g.pendingAction.chosenCompetition = chosenCards
	default:
		return fmt.Errorf("no associated action found")
	}
	return nil
}

func (g *Game) StepOpponentResponse(opponent *Player, observation Observation) error {
	opponentChoice, err := opponent.makeChoice(observation)
	if err != nil {
		return err
	}
	g.pendingAction.opponentChoice = opponentChoice
	return nil
}

func (g *Game) StepResolve(current, opponent *Player) error {
	switch g.pendingAction.action.actionName {
	case SecretName:
		current.save(g.pendingAction.chosenSecret)
	case DiscardName:
		current.discard(g.pendingAction.chosenDiscard)
	case GiftName:
		gifts := g.pendingAction.chosenGift
		opponentToPlay := gifts[g.pendingAction.opponentChoice]
		currentToPlay := append(gifts[:g.pendingAction.opponentChoice], gifts[g.pendingAction.opponentChoice+1:]...)
		g.playCard(opponent, opponentToPlay)
		g.playMultipleCards(current, currentToPlay)
		current.removeFromHand(gifts)
	case CompetitionName:
		sets := [][]Suit{g.pendingAction.chosenCompetition[0:2], g.pendingAction.chosenCompetition[2:]}
		opponentToPlay := sets[g.pendingAction.opponentChoice]
		currentToPlay := sets[g.pendingAction.opponentChoice^1] // xor
		g.playMultipleCards(opponent, opponentToPlay)
		g.playMultipleCards(current, currentToPlay)
		current.removeFromHand(g.pendingAction.chosenCompetition)
	default:
		return fmt.Errorf("action not found!")
	}
	g.pendingAction = &PendingAction{}
	return nil
}
