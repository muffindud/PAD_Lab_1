package com.example.game

import com.example.models.Card
import com.example.models.Rank
import com.example.models.Suit

class GameManager {
    var deck: MutableList<Card> = mutableListOf<Card>()

    init {
        resetGame()
        shuffleDeck()
    }

    fun resetGame() {
        for (i in 0..4) {
            for (suit in Suit.entries) {
                for (rank in Rank.entries) {
                    deck.add(Card(suit, rank))
                }
            }
        }
    }

    fun shuffleDeck() {
        deck.shuffle()
        deck.shuffle()
        deck.shuffle()
    }

    fun getTopCard(): Card {
        return deck.removeAt(0)
    }

    fun showDeck() {
        for (card in deck) {
            println(card.toString())
        }
    }
}

fun getScore(cards: MutableList<Card>): Int {
    var score = 0
    var aceCount = 0
    for (card in cards) {
        when (card.rank) {
            Rank.ACE -> {
                score += 11
                aceCount++
            }
            Rank.TWO -> score += 2
            Rank.THREE -> score += 3
            Rank.FOUR -> score += 4
            Rank.FIVE -> score += 5
            Rank.SIX -> score += 6
            Rank.SEVEN -> score += 7
            Rank.EIGHT -> score += 8
            Rank.NINE -> score += 9
            Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING -> score += 10
        }
    }
    while (score > 21 && aceCount > 0) {
        score -= 10
        aceCount--
    }
    return score
}
