package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class PlayerStateChange(val username: String, val card: Card) {
    override fun toString(): String {
        return "PlayerStateChange(username='$username', card=$card)"
    }
}
