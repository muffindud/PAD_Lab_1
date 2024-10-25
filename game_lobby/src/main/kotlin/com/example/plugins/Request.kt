package com.example.plugins

import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*

val client = HttpClient(CIO)
suspend fun getResponse(): HttpResponse
{
    return client.get("http://example.com")
}
