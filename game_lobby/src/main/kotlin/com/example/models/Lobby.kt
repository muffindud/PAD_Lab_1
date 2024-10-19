package com.example.models

import io.ktor.websocket.*

class Lobby {
    val clients = mutableListOf<DefaultWebSocketSession>()

    fun addClient(client: DefaultWebSocketSession) {
        clients.add(client)
    }

    fun removeClient(client: DefaultWebSocketSession) {
        clients.remove(client)
    }

    suspend fun broadcast(message: String) {
        clients.forEach { client ->
            client.send(message)
        }
    }
}
