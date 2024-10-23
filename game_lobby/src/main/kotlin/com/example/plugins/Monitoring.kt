package com.example.plugins

import io.ktor.server.application.*
import io.ktor.server.plugins.callloging.*
import io.ktor.server.plugins.origin
import io.ktor.server.request.*
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

fun Application.configureMonitoring() {
    install(CallLogging) {
        format { call ->
            val remoteHost = call.request.origin.remoteHost
            val method = call.request.httpMethod.value
            val uri = call.request.uri
            val protocol = call.request.httpVersion
            val status = call.response.status()?.value ?: "-"
            val userAgent = call.request.headers["User-Agent"] ?: "unknown"
            val dateFormat = SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss z", Locale.ENGLISH)
            val date = dateFormat.format(Date())
            "$remoteHost - - [$date] \"$method $uri $protocol\" $status - \"$userAgent\""
        }
    }
}
