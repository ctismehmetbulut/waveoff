package com.demo.demo

import android.Manifest
import android.content.Intent
import android.graphics.Bitmap
import android.os.Bundle
import android.telecom.TelecomManager
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.core.app.ActivityCompat
import androidx.lifecycle.Observer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class GestureResponse(
    val result: ResultData,
    val previous_result: ResultData,
    val unchanged_count: Int
)

@Serializable
data class ResultData(
    val hand_sign: String
)

class MainActivity : ComponentActivity() {
    companion object {
        const val SERVER_IP = "192.168.193.91"//"10.20.116.247"
        const val SERVER_PORT = 5000
    }

    private lateinit var videoCaptureBridge: VideoCaptureBridge
    private val flaskConnector = FlaskWebSocketConnector(SERVER_IP, SERVER_PORT).apply {
        onGestureReceived = { gestureResponse ->
            try {
                val parsedResponse: GestureResponse = Json.decodeFromString(gestureResponse)
                println("RAHMAN: Parsed Gesture: ${parsedResponse.unchanged_count}, ${parsedResponse.previous_result.hand_sign} ")
                val handSign = parsedResponse.previous_result.hand_sign;
                if(handSign == "Index" || handSign == "Open"){
                    println("RAHMAN: CALL REJECTED")
                    rejectCall()
                }
            } catch (e: Exception) {
                // Handle parsing errors
                println("Error parsing gesture response: ${e.message}")
            }
        }
    }

    private fun rejectCall() {
        try {
            val telecomManager = getSystemService(TELECOM_SERVICE) as TelecomManager
            telecomManager.endCall() // Requires Android 10+
            Log.d("CallReject", "Call rejected via TelecomManager")
        } catch (e: Exception) {
            Log.e("CallReject", "Failed to reject call: ${e.message}")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        println("RAHMAN-initialize")

        ActivityCompat.requestPermissions(this, arrayOf(
            Manifest.permission.CAMERA, Manifest.permission.RECEIVE_BOOT_COMPLETED,
            Manifest.permission.POST_NOTIFICATIONS,
            Manifest.permission.FOREGROUND_SERVICE_DATA_SYNC,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.FOREGROUND_SERVICE,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.ANSWER_PHONE_CALLS
        ), 0
        )

        videoCaptureBridge = VideoCaptureBridge(this)
        flaskConnector.connect()
        videoCaptureBridge.startCamera(flaskConnector)

        try {
            Intent(applicationContext, ForegroundService::class.java).also{
                it.action = ForegroundService.Actions.START.toString()
                startService(it)
            }
        } catch(error: Error) {
            println("DEMO_ERROR")
            println(error.toString())
            println(error.stackTrace)
            println(error.cause)
            println(error.message)
        }

        setContent {
            var bitmapToShow by remember { mutableStateOf<Bitmap?>(null) }

            // Observe the current bitmap from VideoCaptureBridge
            videoCaptureBridge.currentBitmap.observe(this, Observer { bitmap ->
                bitmapToShow = bitmap
            })

            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                bitmapToShow?.let { bitmap ->
                    Image(
                        bitmap = bitmap.asImageBitmap(),
                        contentDescription = null,
                        modifier = Modifier
                            .graphicsLayer(
                                scaleX = 3f, // Scale width by 1.5x
                                scaleY = -3f, // Scale height by -1.5x (flipped and enlarged)
                                rotationZ = 270f // Rotate the image by 270 degrees
                            )
                            .weight(0.2f) // Makes the image take more space
                    )
                }

                Button(onClick = {
                    try {
                        Intent(applicationContext, ForegroundService::class.java).also{
                            it.action = ForegroundService.Actions.START.toString()
                            startService(it)
                        }
                    } catch(error: Error) {
                        println("DEMO_ERROR")
                        println(error.toString())
                        println(error.stackTrace)
                        println(error.cause)
                        println(error.message)
                    }}) {
                    Text("Enable Notification")
                }
                Button(onClick = {
                    Intent(applicationContext, ForegroundService::class.java).also{
                        it.action = ForegroundService.Actions.STOP.toString()
                        startService(it)
                    }
                }) {
                    Text("Disable Notification")
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        flaskConnector.disconnect()
    }
}
