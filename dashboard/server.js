const express = require('express');
const mqtt = require('mqtt');
const { Server } = require('socket.io');
const http = require('http');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

const mqttClient = mqtt.connect('mqtt://127.0.0.1:1883');

let countdownValue = 60;
let timerInterval = null;
let isRunning = false;

mqttClient.on('connect', () => {
    console.log('Dashboard Engine linked to Mosquitto!');
    mqttClient.subscribe('room/+/heartbeat');
    mqttClient.subscribe('room/+/notifications');
    mqttClient.subscribe('room/control/timer_sync');
});

function broadcastTimeUpdate(time) {
    io.emit('haunted-house-data', { topic: 'room/control/timer_sync', message: time.toString() });
    mqttClient.publish('room/control/timer_sync', time.toString(), { retain: true });
}

mqttClient.on('message', (topic, payload) => {
    io.emit('haunted-house-data', { topic: topic, message: payload.toString() });
});

io.on('connection', (socket) => {
    socket.emit('haunted-house-data', { topic: 'room/control/timer_sync', message: countdownValue.toString() });

    socket.on('timer-control', (data) => {
        if (data.action === 'start') {
            if (isRunning) clearInterval(timerInterval);
            
            countdownValue = data.value;
            isRunning = true;
            console.log(`Starting/Updating timer to: ${countdownValue}s`);
            
            broadcastTimeUpdate(countdownValue);

            timerInterval = setInterval(() => {
                if (countdownValue > 0 && isRunning) {
                    countdownValue--;
                    broadcastTimeUpdate(countdownValue);
                } else {
                    clearInterval(timerInterval);
                    isRunning = false;
                }
            }, 1000);

        } else if (data.action === 'stop') {
            console.log(`Stopping timer at: ${countdownValue}s`);
            isRunning = false;
            clearInterval(timerInterval);
            broadcastTimeUpdate(countdownValue);
        }
    });
});

server.listen(3000, () => { console.log('Dashboard -> http://localhost:3000'); });