package com.demo.demo

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.telecom.TelecomManager
import android.telephony.PhoneStateListener
import android.telephony.TelephonyManager
import android.util.Log
import androidx.core.app.NotificationCompat

class ForegroundService: Service() {
    private lateinit var telephonyManager: TelephonyManager
    private var callStatus = "Idle"

    override fun onBind(intent: Intent?): IBinder? {
        return null;
        //TODO("Not yet implemented")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when(intent?.action){
            Actions.START.toString() -> start()
            Actions.STOP.toString() -> stopSelf()
        }

        return super.onStartCommand(intent, flags, startId)
    }

    private fun start(){

        // Existing notification setup
        val notification = NotificationCompat.Builder(this, "running_channel")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("Run is active")
            .setContentText("Syncing...")
            .build()
        startForeground(1, notification)
        // Initialize TelephonyManager and start listening
        telephonyManager = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
        telephonyManager.listen(phoneStateListener, PhoneStateListener.LISTEN_CALL_STATE)
    }

    private val phoneStateListener = object : PhoneStateListener() {
        override fun onCallStateChanged(state: Int, incomingNumber: String?) {
            Log.d("RunningService", "Call state changed: $state")
            println("MEHMET phoneStateListener -> onCallStateChanged")
            callStatus = when (state) {
                TelephonyManager.CALL_STATE_RINGING -> {
                    // Use DecidePhoneCall as a helper
                    // Send Intent to AccessibilityService to reject the call
                    //val rejectIntent = Intent("com.demo.demo.ACTION_REJECT_CALL")
                    //sendBroadcast(rejectIntent)
                    //rejectCall()
                    "MEHMET - Incoming call from: $incomingNumber"
                }
                TelephonyManager.CALL_STATE_IDLE -> "Idle"
                TelephonyManager.CALL_STATE_OFFHOOK -> "In call"
                else -> "Unknown"
            }
            updateNotification(callStatus)
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


    private fun updateNotification(callStatus: String) {
        val notification = NotificationCompat.Builder(this, "running_channel")
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("Call Status")
            .setContentText(callStatus)
            .build()
        // Update the foreground notification
        startForeground(1, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        telephonyManager.listen(phoneStateListener, PhoneStateListener.LISTEN_NONE)
    }

    enum class Actions{
        START, STOP
    }
}