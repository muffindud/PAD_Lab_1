package com.example.infrastructure.repository

import com.example.domain.entity.GameLog
import com.example.domain.ports.GameLogRepository
import com.mongodb.kotlin.client.coroutine.MongoDatabase
import org.bson.BsonValue
import org.bson.types.ObjectId

class GameLogRepositoryImpl(
    private val mongoDatabase: MongoDatabase
): GameLogRepository {
    companion object {
        const val COLLECTION_NAME = "game_logs"
    }

    override suspend fun insertOne(gameLog: GameLog): BsonValue? {
        TODO("Not yet implemented")
    }

    override suspend fun deleteById(id: ObjectId): Long {
        TODO("Not yet implemented")
    }

    override suspend fun findById(id: ObjectId): GameLog? {
        TODO("Not yet implemented")
    }

    override suspend fun updateOne(id: ObjectId, gameLog: GameLog): Long {
        TODO("Not yet implemented")
    }

    override suspend fun findByLobbyId(lobbyId: ObjectId): List<GameLog> {
        TODO("Not yet implemented")
    }

    override suspend fun findByUsername(username: String): List<GameLog> {
        TODO("Not yet implemented")
    }
}