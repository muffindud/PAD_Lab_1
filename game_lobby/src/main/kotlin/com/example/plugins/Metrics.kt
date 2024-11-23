package com.example.plugins

import io.ktor.server.application.*
import io.ktor.server.metrics.micrometer.*
import io.micrometer.prometheusmetrics.*

fun Application.configureMetrics(): PrometheusMeterRegistry {
    var appMicrometerRegistry = PrometheusMeterRegistry(PrometheusConfig.DEFAULT)

    install(MicrometerMetrics) {
        registry = appMicrometerRegistry
    }

    return appMicrometerRegistry
}