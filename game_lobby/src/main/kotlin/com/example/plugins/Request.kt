package com.example.plugins

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.net.InetAddress

@Serializable
data class ServiceDiscoveryResponse(val service_id: String, val message: String)

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

fun getContainerPort(): Int? {
    return runBlocking {
        // Send a GET request to the Docker API
        val response: HttpResponse = client.get("http://localhost:2375/containers/self/json") // Docker API endpoint

        // Use bodyAsText() to get the response body as a string
        val containerInfo = response.bodyAsText() // Read the response body

        // Parse the JSON response
        val jsonElement = Json.parseToJsonElement(containerInfo) // Parse the string to a JsonElement
        val jsonObject = jsonElement.jsonObject // Cast to JsonObject

        // Accessing the Ports information
        val ports = jsonObject["NetworkSettings"]?.jsonObject?.get("Ports")?.jsonObject

        // Extracting the specific port mapping
        val portMapping = ports?.get("8080/tcp")?.jsonArray?.get(0)?.jsonObject // Get the first mapping

        // Get the HostPort value
        val hostPort = portMapping?.get("HostPort")?.jsonPrimitive?.content?.toInt()

        hostPort // Return the port number
    }
}
