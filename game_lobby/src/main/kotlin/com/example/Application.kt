package com.example

import com.example.plugins.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry

val game_lobby_port = System.getenv("GAME_LOBBY_PORT").toInt()

// TODO: Get from service discovery
//val user_manager_host = System.getenv("USER_MANAGER_HOST")
//val user_manager_port = System.getenv("USER_MANAGER_PORT").toInt()

val jwt_internal_secret = System.getenv("JWT_INTERNAL_SECRET")
val jwt_user_secret = System.getenv("JWT_USER_SECRET")
val mongo_uri = "mongodb://${System.getenv("MONGO_ROOT_USER")}:${System.getenv("MONGO_ROOT_PASS")}@${System.getenv("MONGO_HOST")}:${System.getenv("MONGO_PORT")}"
val mongo_name = System.getenv("MONGO_DB_NAME")
val service_discovery_url = "http://${System.getenv("SERVICE_DISCOVERY_HOST")}:${System.getenv("SERVICE_DISCOVERY_PORT")}/discovery"

var serviceId: String = ""

const val serviceName: String = "Game Lobby"

var externalPort: Int = 0

suspend fun main(args: Array<String>) {
    externalPort = getPort(service_discovery_url)
    serviceId = registerService(service_discovery_url, game_lobby_port)
    embeddedServer(
        Netty,
        port = game_lobby_port,
        host = "0.0.0.0",
        module = Application::module
    )
        .start(wait = true)
}

fun Application.module() {
    configureMongo(mongo_uri, mongo_name)
    val appMicrometerRegistry: PrometheusMeterRegistry = configureMetrics()
    configureSecurity(jwt_user_secret, jwt_internal_secret)
    val getActiveLobbies: () -> MutableMap<Int, List<String>> = configureSockets()
    configureMonitoring()
    configureRouting(externalPort, appMicrometerRegistry, { getActiveLobbies() })
}
