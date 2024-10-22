package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class PlayerAction(val username: String, val action: ActionType) {
    override fun toString(): String {
        return "PlayerAction(username='$username', action=$action)"
    }
}

@Serializable
enum class ActionType {
    HIT,
    STAND,
    DOUBLE,
    SPLIT,
    SURRENDER
}
