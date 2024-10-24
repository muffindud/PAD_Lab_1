package com.example.domain.ports

import com.example.domain.entity.GameLog
import org.bson.BsonValue
import org.bson.types.ObjectId

interface GameLogRepository {
    suspend fun insertOne(gameLog: GameLog): BsonValue?

    suspend fun deleteById(objectId: ObjectId): Long
    suspend fun findById(objectId: ObjectId): GameLog?
    suspend fun updateOne(objectId: ObjectId, gameLog: GameLog): Long

    suspend fun findByLobbyId(lobbyId: String): List<GameLog>
    suspend fun findByUsername(username: String): List<GameLog>
}
