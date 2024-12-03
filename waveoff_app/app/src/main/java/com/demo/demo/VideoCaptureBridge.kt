package com.demo.demo

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Size
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.MutableLiveData
import android.graphics.ImageFormat
import java.io.ByteArrayOutputStream
import android.graphics.YuvImage
import android.graphics.Rect

class VideoCaptureBridge(private val context: Context) {
    companion object {
        const val WIDTH = 256 // Compile-time constant
        const val HEIGHT = 144
    }

    private var imageAnalysis: ImageAnalysis? = null
    val currentBitmap = MutableLiveData<Bitmap?>()

    // Initialize CameraX and start capturing frames
    fun startCamera(flaskConnector: FlaskWebSocketConnector) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            imageAnalysis = ImageAnalysis.Builder()
                .setTargetResolution(Size(WIDTH, HEIGHT))
                //.setTargetRotation(Surface.ROTATION_180)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also { analysis ->
                    analysis.setAnalyzer(ContextCompat.getMainExecutor(context)) { imageProxy ->
                        val byteArrayData = imageProxyToBGR(imageProxy)
                        // SEND BGR DATA TO FLASK SERVER
                        flaskConnector.sendBGRData(byteArrayData)
                        handleFrame(imageProxy)
                    }
                }

            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    context as androidx.lifecycle.LifecycleOwner, cameraSelector, imageAnalysis
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }, ContextCompat.getMainExecutor(context))
    }

    private fun imageProxyToBGR(image: ImageProxy): ByteArray {
        val yBuffer = image.planes[0].buffer // Y plane
        val uBuffer = image.planes[1].buffer // U plane
        val vBuffer = image.planes[2].buffer // V plane

        val yRowStride = image.planes[0].rowStride
        val uvRowStride = image.planes[1].rowStride
        val uvPixelStride = image.planes[1].pixelStride

        // Prepare the BGR byte array
        val bgrArray = ByteArray(WIDTH * HEIGHT * 3) // Final size: 256 * 144 * 3
        var bgrIndex = 0

        for (j in 0 until HEIGHT) {
            for (i in 0 until WIDTH) {
                // Extract Y value
                val y = (yBuffer[j * yRowStride + i].toInt() and 0xFF)

                // Calculate UV offsets based on subsampling
                val uvIndex = (j / 2) * uvRowStride + (i / 2) * uvPixelStride
                val u = (uBuffer[uvIndex].toInt() and 0xFF)
                val v = (vBuffer[uvIndex].toInt() and 0xFF)

                // YUV to BGR conversion
                val r = (y + 1.370705 * (v - 128)).toInt().coerceIn(0, 255)
                val g = (y - 0.337633 * (u - 128) - 0.698001 * (v - 128)).toInt().coerceIn(0, 255)
                val b = (y + 1.732446 * (u - 128)).toInt().coerceIn(0, 255)

                // Store BGR values
                bgrArray[bgrIndex++] = b.toByte()
                bgrArray[bgrIndex++] = g.toByte()
                bgrArray[bgrIndex++] = r.toByte()
            }
        }

        //image.close() // Release resources for this frame
        return bgrArray
    }

    private fun imageProxyToBitmap(image: ImageProxy): Bitmap? {
        val nv21 = yuv420888ToNv21(image)
        val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(Rect(0, 0, yuvImage.width, yuvImage.height), 100, out)
        val imageBytes = out.toByteArray()
        return BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
    }
    private fun yuv420888ToNv21(image: ImageProxy): ByteArray {
        val width = image.width
        val height = image.height
        val ySize = width * height
        val uvSize = width * height / 2
        val nv21 = ByteArray(ySize + uvSize)
        val yBuffer = image.planes[0].buffer
        val uBuffer = image.planes[1].buffer
        val vBuffer = image.planes[2].buffer
        val yRowStride = image.planes[0].rowStride
        val yPixelStride = image.planes[0].pixelStride
        val uRowStride = image.planes[1].rowStride
        val uPixelStride = image.planes[1].pixelStride
        val vRowStride = image.planes[2].rowStride
        val vPixelStride = image.planes[2].pixelStride
        var pos = 0
        // Extract Y plane
        for (row in 0 until height) {
            for (col in 0 until width) {
                nv21[pos++] = yBuffer.get(row * yRowStride + col * yPixelStride)
            }
        }
        // Extract V and U planes; NV21 format is YUV with V and U interleaved
        val uvHeight = height / 2
        for (row in 0 until uvHeight) {
            for (col in 0 until width / 2) {
                nv21[pos++] = vBuffer.get(row * vRowStride + col * vPixelStride)
                nv21[pos++] = uBuffer.get(row * uRowStride + col * uPixelStride)
            }
        }
        return nv21
    }

    // Process each frame and update the current Bitmap
    private fun handleFrame(imageProxy: ImageProxy) {
        val bitmap = imageProxyToBitmap(imageProxy)
        currentBitmap.postValue(bitmap) // Update LiveData with the new bitmap
        imageProxy.close()  // Release frame resources
    }
}
