package com.example.domain.entity

import com.example.application.response.GameLogResponse
import org.bson.codecs.pojo.annotations.BsonId
import org.bson.types.ObjectId

data class GameLog(
    @BsonId val id: ObjectId,
    val lobbyId: String,
    val gameActions: Collection<String>
) {
    fun toResponse() = GameLogResponse(
        id = id.toString(),
        lobbyId = lobbyId,
        gameActions = gameActions
    )
}
