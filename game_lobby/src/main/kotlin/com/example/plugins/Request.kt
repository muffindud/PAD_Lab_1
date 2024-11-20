package com.example.plugins

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json
import kotlinx.serialization.Serializable
import java.net.InetAddress

@Serializable
data class ServiceDiscoveryResponse(val service_id: String, val message: String)

@Serializable
data class ServiceDiscoveryPort(val port: Int)

val client = HttpClient(CIO) {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true // in case the JSON response has more fields than your data class
        })
    }
}

suspend fun registerService(serviceDiscoveryUrl: String, port: Int): String
{
    println("Registering service as ${InetAddress.getLocalHost().hostName}:$port")
    val response: HttpResponse = client.post(urlString = serviceDiscoveryUrl) {
        contentType(ContentType.Application.Json)
        setBody(
            """
            {
                "service_name": "Game Lobby",
                "host": "${InetAddress.getLocalHost().hostName}",
                "port": "$port"
            }
            """.trimIndent()
        )
    }

    val responseJson: ServiceDiscoveryResponse = response.body()

    return responseJson.service_id
}

suspend fun getPort(serviceDiscoveryUrl: String): Int
{
    println("Requesting port from service discovery")
    val response: HttpResponse = client.get(urlString = "${serviceDiscoveryUrl}/get_lobby_port") {
        contentType(ContentType.Application.Json)
    }

    val responseJson: ServiceDiscoveryPort = response.body()

    return responseJson.port
}
