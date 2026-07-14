package com.example.testing_notification

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.eclipse.paho.client.mqttv3.*
import java.util.UUID
import kotlin.math.roundToInt
import com.example.testing_notification.ui.theme.*

class MainActivity : ComponentActivity() {

    private lateinit var mqttClient: MqttClient
    private val brokerUrl = "tcp://100.71.35.180:1883"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = Color(0xFF121212)
            ) {
                SHHScreen()
            }
        }
    }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    fun SHHScreen() {
        var emergencyAlertText by remember { mutableStateOf("") }
        var liveSyncTime by remember { mutableStateOf(60) }
        val playerOptions = remember { listOf("Player 1", "Player 2", "Player 3") }
        var expanded by remember { mutableStateOf(false) }
        var selectedPlayer by remember { mutableStateOf(playerOptions[0]) }

        var statusText by remember { mutableStateOf("Status: Disconnected") }
        var statusColor by remember { mutableStateOf(Color.Gray) }
        var notificationText by remember { mutableStateOf("Waiting") }
        var isConnected by remember { mutableStateOf(false) }

        var heartbeatBpm by remember { mutableStateOf(60f) }

        val coroutineScope = rememberCoroutineScope()

        Box(
            modifier = Modifier.fillMaxSize().padding(32.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (emergencyAlertText.isNotBlank()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color.Red)
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = emergencyAlertText,
                            color = Color.White,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.ExtraBold,
                            textAlign = TextAlign.Center
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }
                Text(
                    text = "SHH!!!",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.Red,
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                ExposedDropdownMenuBox(
                    expanded = expanded,
                    onExpandedChange = { if (!isConnected) expanded = !expanded },
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    OutlinedTextField(
                        value = selectedPlayer,
                        onValueChange = {},
                        readOnly = true,
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            focusedBorderColor = Color.Red,
                            unfocusedBorderColor = Color.DarkGray,
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent
                        ),
                        modifier = Modifier.menuAnchor().fillMaxWidth()
                    )
                    ExposedDropdownMenu(
                        expanded = expanded,
                        onDismissRequest = { expanded = false }
                    ) {
                        playerOptions.forEach { item ->
                            DropdownMenuItem(
                                text = { Text(text = item) },
                                onClick = {
                                    selectedPlayer = item
                                    expanded = false
                                }
                            )
                        }
                    }
                }

                Button(
                    onClick = {
                        if (isConnected) {
                            coroutineScope.launch(Dispatchers.IO) {
                                try {
                                    if (::mqttClient.isInitialized && mqttClient.isConnected) {
                                        mqttClient.disconnect()
                                    }
                                    isConnected = false
                                    statusText = "Status: Disconnected"
                                    statusColor = Color.Gray
                                    notificationText = "Waiting"
                                } catch (e: MqttException) {
                                    e.printStackTrace()
                                }
                            }
                        } else {
                            val topicId = selectedPlayer.replace(" ", "").lowercase()

                            coroutineScope.launch(Dispatchers.IO) {
                                try {
                                    val clientId = UUID.randomUUID().toString()
                                    mqttClient = MqttClient(brokerUrl, clientId, null)
                                    val options = MqttConnectOptions().apply {
                                        isAutomaticReconnect = true
                                        isCleanSession = true
                                    }
                                    mqttClient.connect(options)

                                    isConnected = true
                                    statusText = "Connected as: $selectedPlayer"
                                    statusColor = Color.Green

                                    // Switch subscriptions over to the house/ ecosystem layout
                                    mqttClient.subscribe("house/timers/timer_sync") { _, message ->
                                        val incomingTime = String(message.payload).toIntOrNull() ?: 60
                                        runOnUiThread {
                                            liveSyncTime = incomingTime
                                        }
                                    }
                                    mqttClient.subscribe("house/players/$topicId/notifications") { _, message ->
                                        notificationText = String(message.payload)
                                    }

                                    mqttClient.subscribe("house/alerts/emergency") { _, message ->
                                        val alert = String(message.payload)
                                        runOnUiThread {
                                            if (alert == "CLEAR") {
                                                emergencyAlertText = ""
                                            } else {
                                                emergencyAlertText = alert
                                            }
                                        }
                                    }

                                } catch (e: MqttException) {
                                    e.printStackTrace()
                                    statusText = "Connection Failed!"
                                    statusColor = Color.Red
                                }
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isConnected) Color(0xFF441111) else Color.Red
                    ),
                    modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)
                ) {
                    Text(
                        text = if (isConnected) "Disconnect" else "Connect",
                        color = Color.White
                    )
                }

                Text(
                    text = statusText,
                    color = statusColor,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 32.dp)
                )
                if (isConnected) {
                    val mins = liveSyncTime / 60
                    val secs = liveSyncTime % 60
                    val formattedClock = String.format("%02d:%02d", mins, secs)

                    Text(
                        text = "TIME LEFT: $formattedClock",
                        color = if (liveSyncTime <= 5) Color.Red else Pink80,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(bottom = 24.dp)
                    )
                }
                if (isConnected) {
                    Text(text = "Heart Rate: ${heartbeatBpm.roundToInt()} BPM", color = Color.White)
                    Slider(
                        value = heartbeatBpm,
                        onValueChange = { heartbeatBpm = it },
                        valueRange = 60f..180f,
                        colors = SliderDefaults.colors(thumbColor = Color.Red, activeTrackColor = Color.Red),
                        onValueChangeFinished = {
                            val topicId = selectedPlayer.replace(" ", "").lowercase()
                            val heartbeatTopic = "house/players/$topicId/heartbeat"
                            val payload = heartbeatBpm.roundToInt().toString()

                            coroutineScope.launch(Dispatchers.IO) {
                                if (::mqttClient.isInitialized && mqttClient.isConnected) {
                                    mqttClient.publish(heartbeatTopic, MqttMessage(payload.toByteArray()))
                                }
                            }
                        },
                        modifier = Modifier.padding(bottom = 32.dp)
                    )
                }

                if (notificationText.isNotBlank() && notificationText != "Waiting") {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF222222))
                            .padding(20.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = notificationText,
                            color = Color.White,
                            fontSize = 16.sp,
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::mqttClient.isInitialized && mqttClient.isConnected) {
            mqttClient.disconnect()
        }
    }
}