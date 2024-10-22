package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class GameStateChange(val state: GameState)

@Serializable
enum class GameState {
    OPEN_BET,
    CLOSE_BET,
    OPEN_ACTION,
    CLOSE_ACTION
}
