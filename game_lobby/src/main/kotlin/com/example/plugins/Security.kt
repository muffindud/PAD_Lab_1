package com.example.plugins

import com.auth0.jwt.JWT
import com.auth0.jwt.algorithms.Algorithm
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.auth.jwt.*
import io.ktor.server.response.*

fun Application.configureSecurity(userJWT: String, serverJWT: String) {
    authentication {
        jwt("user_jwt") {
            verifier(JWT
                .require(Algorithm.HMAC256(userJWT))
                .build()
            )
            validate {
                val username = it.payload.getClaim("username").asString()
                if (username != null) {
                    JWTPrincipal(it.payload)
                } else {
                    null
                }
            }
            challenge { _, _ ->
                call.respond(HttpStatusCode.Unauthorized, "Unauthorized")
            }
        }

        jwt("server_jwt") {
            verifier(JWT
                .require(Algorithm.HMAC256(serverJWT))
                .build()
            )
            validate {
                val server = it.payload.getClaim("server").asString()
                if (server != null) {
                    JWTPrincipal(it.payload)
                } else {
                    null
                }
            }
            challenge { _, _ ->
                call.respond(HttpStatusCode.Unauthorized, "Unauthorized")
            }
        }
    }
}
