package com.example.models

import ch.qos.logback.core.net.server.Client
import com.example.game.GameManager
import io.ktor.websocket.*

class Lobby {
    val clients = mutableListOf<DefaultWebSocketSession>()
    val gameManager: GameManager = GameManager()

    fun addClient(client: DefaultWebSocketSession) {
        clients.add(client)
    }

    fun removeClient(client: DefaultWebSocketSession) {
        clients.remove(client)
    }

    suspend fun handleCommand(command: String, client: DefaultWebSocketSession, username: String? = null) {
        // TODO: Handle commands
        if (username == null) {
            broadcast(command)
        } else {
            broadcast("$username: $command")
        }
    }

    suspend fun broadcast(message: String) {
        clients.forEach { client ->
            client.send(message)
        }
    }
}
