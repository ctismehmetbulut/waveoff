package com.demo.demo

import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import android.util.Base64

class FlaskWebSocketConnector(private val serverIp: String, private val port: Int) {
    private var webSocketClient: WebSocketClient? = null
    var onGestureReceived: ((String) -> Unit)? = null

    // Establish WebSocket connection (reuse if already connected).
    fun connect() {
        if (webSocketClient != null && webSocketClient!!.isOpen) {
            println("RAHMAN: WebSocket already connected.")
            return
        }

        val webSocketUrl = "ws://$serverIp:$port/opencv"
        println("RAHMAN: Attempting to connect to WebSocket at: $webSocketUrl")

        try {
            webSocketClient = object : WebSocketClient(URI(webSocketUrl)) {
                override fun onOpen(handshakedata: ServerHandshake?) {
                    println("RAHMAN: WebSocket connected successfully!")
                }

                override fun onMessage(message: String?) {
                    message?.let {
                        //println("RAHMAN: Response from server: $it")
                        onGestureReceived?.invoke(it) // Trigger callback with server response
                    } ?: run {
                        println("RAHMAN: Received null message from server.")
                    }
                }

                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    println("RAHMAN: WebSocket connection closed. Reason: $reason")
                }

                override fun onError(ex: Exception?) {
                    ex?.let {
                        println("RAHMAN: WebSocket error: ${it.message}")
                    }
                }
            }
            webSocketClient?.connect()
            println("RAHMAN: Connecting to WebSocket...")
        } catch (e: Exception) {
            println("RAHMAN: Error initializing WebSocket: ${e.message}")
        }
    }

    fun sendBGRData(byteArrayData: ByteArray) {
        if (webSocketClient == null || !webSocketClient!!.isOpen) {
            println("RAHMAN: WebSocket not connected. Connecting now...")
            connect()
        }

        try {
            // Encode the byte array to Base64
            val base64Data = Base64.encodeToString(byteArrayData, Base64.NO_WRAP)

            // Send the encoded data
            webSocketClient?.send(base64Data)
            //println("RAHMAN: Sent BGR data in Base64 format")
            println("Base64 size: ${base64Data.length}")
        } catch (e: Exception) {
            println("RAHMAN: Error sending BGR data: ${e.message}")
        }
    }

    // Disconnect the WebSocket if needed.
    fun disconnect() {
        try {
            webSocketClient?.close()
            webSocketClient = null
            println("RAHMAN: WebSocket disconnected.")
        } catch (e: Exception) {
            println("RAHMAN: Error during WebSocket disconnect: ${e.message}")
        }
    }
}