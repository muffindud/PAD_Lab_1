package com.example.application.response

data class GameLogResponse(
    val id: String,
    val lobbyId: String,
    val gameActions: Collection<String>
)
