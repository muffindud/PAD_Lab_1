package com.example

import com.example.plugins.*
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import kotlinx.coroutines.runBlocking

var game_lobby_port: Int = 8000
var user_manager_host: String = "user_manager"
var user_manager_port: Int = 3000
var jwt_internal_secret: String = "internal_sike"
var jwt_user_secret: String = "sike"

fun main(args: Array<String>) {
    try {
        game_lobby_port = System.getenv("GAME_LOBBY_PORT").toInt()
        user_manager_host = System.getenv("USER_MANAGER_HOST")
        user_manager_port = System.getenv("USER_MANAGER_PORT").toInt()
        jwt_internal_secret = System.getenv("JWT_INTERNAL_SECRET")
        jwt_user_secret = System.getenv("JWT_USER_SECRET")
    } catch (e: Exception) {
        game_lobby_port = 8000
        user_manager_host = "user_manager"
        user_manager_port = 3000
        jwt_internal_secret = "internal_sike"
        jwt_user_secret = "sike"
    }

    embeddedServer(
        Netty,
        port = game_lobby_port,
        host = "0.0.0.0",
        module = Application::module
    )
        .start(wait = true)
}

fun Application.module() {
    configureSockets()
    configureMonitoring()
    configureRouting()
    configureSecurity(jwt_user_secret, jwt_internal_secret)
}
