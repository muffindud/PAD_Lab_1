package com.example.plugins

import io.ktor.http.HttpStatusCode
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.withTimeout

suspend fun <T> executeWithTimeout(block: suspend () -> T): T {
    return withTimeout(3000) {
        block()
    }
}

fun Application.configureRouting() {
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
    }
}
