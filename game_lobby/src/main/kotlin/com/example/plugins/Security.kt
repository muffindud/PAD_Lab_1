package com.example.plugins

import com.auth0.jwt.JWT
import com.auth0.jwt.algorithms.Algorithm
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.auth.jwt.*
import io.ktor.server.response.*

fun Application.configureSecurity(userJWT: String, serverJWT: String) {
    // Please read the jwt property from the config file if you are using EngineMain
    val jwtAudience = "jwt-audience"
    val jwtDomain = "https://jwt-provider-domain/"
    val jwtRealm = "ktor sample app"
    authentication {
        jwt("user_jwt") {
            verifier(JWT
                .require(Algorithm.HMAC256(userJWT))
                .withAudience(jwtAudience)
                .withIssuer(jwtDomain)
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
            challenge { defaultScheme, realm ->
                call.respond(HttpStatusCode.Unauthorized, "Unauthorized")
            }
        }

        jwt("server_jwt") {
            verifier(JWT
                .require(Algorithm.HMAC256(serverJWT))
                .withAudience(jwtAudience)
                .withIssuer(jwtDomain)
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
            challenge { defaultScheme, realm ->
                call.respond(HttpStatusCode.Unauthorized, "Unauthorized")
            }
        }
    }
}
