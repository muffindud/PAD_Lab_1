package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class PlayerBet(val username: String, val bet: Int) {
    override fun toString(): String {
        return "PlayerBet(username='$username', bet=$bet)"
    }
}
