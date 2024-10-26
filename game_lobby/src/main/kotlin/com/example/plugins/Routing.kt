package com.example.plugins

import com.example.domain.ports.GameLogRepository
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.*
import io.ktor.server.auth.authenticate
import io.ktor.server.auth.jwt.JWTPrincipal
import io.ktor.server.auth.principal
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.withTimeout
import org.koin.ktor.ext.inject

suspend fun <T> executeWithTimeout(block: suspend () -> T): T {
    return withTimeout(3000) {
        block()
    }
}

fun Application.configureRouting(getActiveLobbies: () -> MutableMap<Int, List<String>>) {
    val logRepository by inject<GameLogRepository>()

    routing {
        get("/") {
            call.respondText("HELLO WORLD!")
        }

        get("/health") {
            try {
                val result = executeWithTimeout {
                    "{\"status\": \"healthy\"}"
                }
                call.respond(result)
            } catch (e: TimeoutCancellationException) {
                call.respond(HttpStatusCode.RequestTimeout, "{\"status\": \"unhealthy\"}")
            }
        }

        authenticate("user_jwt") {
            get("/logs") {
                val username = call.principal<JWTPrincipal>()?.payload?.getClaim("username")?.asString()

                logRepository.findByUsername(username!!)
                    .let { call.respond(it) }
            }
        }

        authenticate("server_jwt") {
            get("/lobby") {
                val server = call.principal<JWTPrincipal>()?.payload?.getClaim("server")?.asString()
                val activeLobbies = getActiveLobbies().map { (lobbyId, players) -> lobbyId to players }.toMap()

                /*
                  create a body for the response
                    {
                        "port": getContainerPort(),
                        "lobbies": activeLobbies
                 */
                val body = "{\"port\": ${getContainerPort()}, \"lobbies\": $activeLobbies}"

                if (server == "Gateway") {
                    call.respond(
                        HttpStatusCode.OK,
                        body
                    )
                } else {
                    call.respond(HttpStatusCode.Forbidden)
                }
            }
        }
    }
}
