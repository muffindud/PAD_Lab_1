package com.example.plugins

import io.ktor.http.HttpHeaders
import io.ktor.serialization.kotlinx.KotlinxWebsocketSerializationConverter
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.websocket.*
import io.ktor.websocket.*
import java.time.*

fun Application.configureSockets() {
    install(WebSockets) {
        // TODO: Adjust values
        pingPeriod = Duration.ofSeconds(15)
        timeout = Duration.ofSeconds(15)
        maxFrameSize = Long.MAX_VALUE
        masking = false

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
        webSocket("/connect/{game_id}") {
            val gameId = call.parameters["game_id"]
            if (gameId == null) {
                // TODO: Get a random game id
                return@webSocket
            }
            send("Connected to game $gameId")
        }
    }
}
