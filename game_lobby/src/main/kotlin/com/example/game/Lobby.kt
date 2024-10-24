package com.example.game

import com.example.application.request.GameLogRequest
import com.example.application.request.toDomain
import com.example.domain.entity.GameLog
import com.example.domain.ports.GameLogRepository
import io.ktor.websocket.*

class Lobby(val lobbyId: String, val logRepository: GameLogRepository, val deleteLobbyInstanceCallback: () -> Unit) {
    val clients = mutableListOf<DefaultWebSocketSession>()
    val gameManager: GameManager = GameManager()
    val gameLog: Collection<String> = emptyList()

    fun addClient(client: DefaultWebSocketSession) {
        clients.add(client)
    }

    suspend fun removeClient(client: DefaultWebSocketSession) {
        clients.remove(client)

        if (clients.isEmpty()) {
            val gameLogRequest = GameLogRequest(
                lobbyId = lobbyId,
                gameActions = gameLog.toList()
            )
            val result = logRepository.insertOne(gameLogRequest.toDomain())
            deleteLobbyInstanceCallback()
        }
    }

    suspend fun handleCommand(command: String, client: DefaultWebSocketSession, username: String? = null) {
        // TODO: Handle commands
        if (username == null) {
            broadcast(command)
        } else {
            gameLog.plus("$username: $command")
            broadcast("$username: $command")
        }
    }

    suspend fun broadcast(message: String) {
        clients.forEach { client ->
            client.send(message)
        }
    }
}
