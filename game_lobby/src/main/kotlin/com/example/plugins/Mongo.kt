package com.example.plugins

import com.example.domain.ports.GameLogRepository
import com.example.infrastructure.repository.GameLogRepositoryImpl
import com.mongodb.kotlin.client.coroutine.MongoClient
import io.ktor.serialization.gson.gson
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import org.koin.dsl.module
import org.koin.ktor.plugin.Koin

fun Application.configureMongo(mongoURI: String, dbName: String) {
    install(ContentNegotiation) {
        gson {}
    }

    install(Koin) {
        modules(module {
            single { MongoClient.create(
                mongoURI
            ) }
            single {
                get<MongoClient>().getDatabase(dbName)
            }
        }, module {
            single<GameLogRepository> { GameLogRepositoryImpl(get()) }
        })
    }
}
