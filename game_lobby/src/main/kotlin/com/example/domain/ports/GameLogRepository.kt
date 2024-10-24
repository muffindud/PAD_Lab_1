package com.example.domain.ports

import com.example.domain.entity.GameLog
import org.bson.BsonValue
import org.bson.types.ObjectId

interface GameLogRepository {
    suspend fun insertOne(gameLog: GameLog): BsonValue?

    suspend fun deleteById(id: ObjectId): Long
    suspend fun findById(id: ObjectId): GameLog?
    suspend fun updateOne(id: ObjectId, gameLog: GameLog): Long

    suspend fun findByLobbyId(lobbyId: ObjectId): List<GameLog>
    suspend fun findByUsername(username: String): List<GameLog>
}
