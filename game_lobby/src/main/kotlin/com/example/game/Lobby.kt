package com.example.game

import com.example.application.request.GameLogRequest
import com.example.application.request.toDomain
import com.example.domain.ports.GameLogRepository
import io.ktor.websocket.*

class Lobby(val lobbyId: String, val logRepository: GameLogRepository, val deleteLobbyInstanceCallback: () -> Unit) {
    val clients = mutableMapOf<DefaultWebSocketSession, String>()
    val gameManager: GameManager = GameManager()
    val gameLog: MutableList<String> = mutableListOf()

    fun addClient(client: DefaultWebSocketSession, username: String) {
        clients.put(client, username)
    }

    fun getUsernames(): List<String> {
        return clients.values.toList()
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

    suspend fun handleCommand(command: String, client: DefaultWebSocketSession) {
        // TODO: Handle commands
        val username = clients[client]
        if (username == null) {
            broadcast(command)
        } else {
            gameLog.add("$username: $command")
            broadcast("$username: $command")
        }
    }

    suspend fun broadcast(message: String) {
        clients.forEach { (client, _) ->
            client.send(message)
        }
    }
}
