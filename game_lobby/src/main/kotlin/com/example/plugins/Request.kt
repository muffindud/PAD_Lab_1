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
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetAddress
import java.io.File


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

suspend fun getExternalPort(): Int {
    val containerId = getContainerId()

    val response: HttpResponse = client.get(urlString = "http://host.docker.internal:2375/containers/$containerId/json") {
        contentType(ContentType.Application.Json)
    }

    val responseJson: String = response.bodyAsText()

//    val port = Regex("\"HostPort\":\"(\\d+)\"").find(responseJson)?.groupValues?.get(1)?.toInt()
    val regex = Regex("\"HostPort\":\"(\\d+)\"")

    val allPorts = regex.findAll(responseJson)
        .map { it.groupValues[1].toInt() } // Extract and convert each HostPort to Int
        .filter { it != 0 }               // Remove entries where HostPort is 0

    val externalPort = allPorts.first()

    return externalPort
}

fun getContainerId(): String? {
    val cgroupFile = File("/proc/self/cgroup")
    if (cgroupFile.exists()) {
        val lines = cgroupFile.readLines()
        for (line in lines) {
            if (line.contains("docker")) {
                val parts = line.split("/")
                return parts.lastOrNull() // The last part should be the container ID
            }
        }
    }
    return null // Not running in a Docker container
}
