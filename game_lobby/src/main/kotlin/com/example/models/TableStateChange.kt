package com.example.models

import kotlinx.serialization.Serializable

@Serializable
data class TableStateChange(val card: Card) {
    override fun toString(): String {
        return "TableStateChange(card=$card)"
    }
}
