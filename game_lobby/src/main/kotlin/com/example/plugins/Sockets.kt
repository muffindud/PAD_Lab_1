package com.example.plugins

import com.example.models.Lobby
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
    val lobbies = mutableMapOf<Int, Lobby>()
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
                lobbies.getOrPut(gameId) { Lobby() }.addClient(this)

                // notify other users that user joined
                lobbies[gameId]?.broadcast("[$username] joined the lobby $gameId")
                try {
                    for (frame in incoming) {
                        frame as? Frame.Text ?: continue
                        val receivedText = frame.readText()
                        lobbies[gameId]?.handleCommand(receivedText, this, username)
                    }
                } finally {
                    // Remove from lobby
                    lobbies[gameId]?.removeClient(this)
                }

                // notify other users that user left
                lobbies[gameId]?.broadcast("[$username] left the lobby $gameId")
            }
        }
    }
}
