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

fun Application.configureRouting() {
    val logRepository by inject<GameLogRepository>()

    routing {
        get("/") {
            call.respondText("HELLO WORLD!")
        }

        get("/health") {
            // call.respond("{\"status\": \"healthy\"}")
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
    }
}
