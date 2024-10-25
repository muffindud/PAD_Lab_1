package com.example.infrastructure.repository

import com.example.domain.entity.GameLog
import com.example.domain.ports.GameLogRepository
import com.mongodb.MongoException
import com.mongodb.client.model.Filters
import com.mongodb.client.model.UpdateOptions
import com.mongodb.client.model.Updates
import com.mongodb.kotlin.client.coroutine.MongoDatabase
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.toList
import org.bson.BsonValue
import org.bson.types.ObjectId

class GameLogRepositoryImpl(
    private val mongoDatabase: MongoDatabase
): GameLogRepository {
    companion object {
        const val GAME_LOG_COLLECTION = "game_logs"
    }

    override suspend fun insertOne(gameLog: GameLog): BsonValue? {
        try {
            val result = mongoDatabase
                .getCollection<GameLog>(GAME_LOG_COLLECTION)
                .insertOne(gameLog)
            return result.insertedId
        } catch (e: MongoException) {
            System.err.println("Error: ${e.message}")
        }
        return null
    }

    override suspend fun deleteById(objectId: ObjectId): Long {
        try {
            val result = mongoDatabase
                .getCollection<GameLog>(GAME_LOG_COLLECTION)
                .deleteOne(Filters.eq("_id", objectId))
            return result.deletedCount
        } catch (e: MongoException) {
            System.err.println("Error: ${e.message}")
        }
        return 0
    }

    override suspend fun findById(objectId: ObjectId): GameLog? =
        mongoDatabase.getCollection<GameLog>(GAME_LOG_COLLECTION)
            .withDocumentClass<GameLog>()
            .find(Filters.eq("_id", objectId))
            .firstOrNull()

    override suspend fun updateOne(objectId: ObjectId, gameLog: GameLog): Long {
        try {
            val query = Filters.eq("_id", objectId)
            val updates = Updates.combine(
                Updates.set(GameLog::lobbyId.name, gameLog.lobbyId),
                Updates.set(GameLog::gameActions.name, gameLog.gameActions),
            )
            val options = UpdateOptions()
                .upsert(true)
            val result = mongoDatabase
                .getCollection<GameLog>(GAME_LOG_COLLECTION)
                .updateOne(query, updates, options)
            return result.modifiedCount
        } catch (e: MongoException) {
            System.err.println("Error: ${e.message}")
        }
        return 0
    }

    override suspend fun findByLobbyId(lobbyId: String): List<GameLog> {
        try {
            return mongoDatabase.getCollection<GameLog>(GAME_LOG_COLLECTION)
                .withDocumentClass<GameLog>()
                .find(Filters.eq(GameLog::lobbyId.name, lobbyId))
                .toList()
        } catch (e: MongoException) {
            System.err.println("Error: ${e.message}")
            return emptyList()
        }
    }

    override suspend fun findByUsername(username: String): List<GameLog> {
        // get all the game logs where the username is contained within the strings of the gameActions list
        try {
            val result = mongoDatabase.getCollection<GameLog>(GAME_LOG_COLLECTION)
                .withDocumentClass<GameLog>()
                .find(Filters.regex(GameLog::gameActions.name, ".*$username.*"))
                .toList()
            return result
        } catch (e: MongoException) {
            System.err.println("Error: ${e.message}")
            return emptyList()
        }
    }
}
