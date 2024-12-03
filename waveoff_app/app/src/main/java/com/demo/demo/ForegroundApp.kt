package com.demo.demo

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context

class ForegroundApp: Application() {
    override fun onCreate() {
        super.onCreate();
        val channel = NotificationChannel("running_channel", "Running Notifications",
            NotificationManager.IMPORTANCE_HIGH);
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.createNotificationChannel(channel)
    }
}