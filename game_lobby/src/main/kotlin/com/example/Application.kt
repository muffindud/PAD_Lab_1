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

//val game_lobby_port = System.getenv("GAME_LOBBY_PORT").toInt()
//val user_manager_host = System.getenv("USER_MANAGER_HOST")
//val user_manager_port = System.getenv("USER_MANAGER_PORT").toInt()
//val jwt_internal_secret = System.getenv("JWT_INTERNAL_SECRET")

fun main(args: Array<String>) {
    // embeddedServer(
    //     Netty,
    //     port = game_lobby_port,
    //     host = "0.0.0.0",
    //     module = Application::module
    // )
    //     .start(wait = true)
    runBlocking {
        println(getResponse().bodyAsText())
        client.close()
    }
}

// fun Application.module() {
//     configureSockets()
//     configureMonitoring()
// }
