package com.example.application.request

import com.example.domain.entity.GameLog
import org.bson.codecs.pojo.annotations.BsonId
import org.bson.types.ObjectId

data class GameLogRequest(
    val lobbyId: String,
    val gameActions: Collection<String>
)

fun GameLogRequest.toDomain(): GameLog {
    return GameLog(
        id = ObjectId(),
        lobbyId = lobbyId,
        gameActions = gameActions
    )
}
