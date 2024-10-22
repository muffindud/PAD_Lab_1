package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class Card(val suit: Suit, val rank: Rank) {
    override fun toString(): String {
        return "${rank.name} of ${suit.name}"
    }
}

@Serializable
enum class Suit {
    HEARTS,
    DIAMONDS,
    CLUBS,
    SPADES
}

@Serializable
enum class Rank {
    ACE,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    TEN,
    JACK,
    QUEEN,
    KING
}
