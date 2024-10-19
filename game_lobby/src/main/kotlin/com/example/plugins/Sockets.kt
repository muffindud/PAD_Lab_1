package com.example.plugins

import io.ktor.serialization.kotlinx.KotlinxWebsocketSerializationConverter
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.auth.jwt.*
import io.ktor.server.routing.*
import io.ktor.server.websocket.*
import io.ktor.websocket.*
import kotlinx.serialization.json.Json
import java.time.*

fun Application.configureSockets() {
    val lobbies = mutableMapOf<Int, MutableList<WebSocketSession>>()
    install(WebSockets) {
        // TODO: Adjust values
        pingPeriod = Duration.ofSeconds(15)
        timeout = Duration.ofSeconds(15)
        maxFrameSize = Long.MAX_VALUE
        masking = false
        contentConverter = KotlinxWebsocketSerializationConverter(Json)
    }
    routing {
        webSocket("/echo") {
            send("Echo server")
            for (frame in incoming) {
                frame as? Frame.Text ?: continue
                val receivedText = frame.readText()
                send("You said: $receivedText")
            }
        }
        authenticate("user_jwt") {
            webSocket("/connect/{game_id}") {
                val gameId = call.parameters["game_id"]?.toIntOrNull() ?: return@webSocket close(CloseReason(CloseReason.Codes.CANNOT_ACCEPT, "Invalid game id"))
                val username = call.principal<JWTPrincipal>()?.payload?.getClaim("username")?.asString()

                // save to lobby
                lobbies.getOrPut(gameId) { mutableListOf() }.add(this)

                // notify other users that user joined
                lobbies[gameId]?.forEach { it.send("[$username] joined the lobby $gameId") }
                try {
                    for (frame in incoming) {
                        frame as? Frame.Text ?: continue
                        val receivedText = frame.readText()
                        lobbies[gameId]?.forEach { it.send("[$username] $receivedText") }
                    }
                } finally {
                    // Remove from lobby
                    lobbies[gameId]?.remove(this)
                }

                // notify other users that user left
                lobbies[gameId]?.forEach { it.send("[$username] left the lobby $gameId") }
            }
        }
    }
}
