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

mqttClient.on('connect', () => {
    console.log('Dashboard connected to Mosquitto broker');
    mqttClient.subscribe('house/#');
});

mqttClient.on('message', (topic, payload) => {
    io.emit('haunted-house-data', { topic: topic, message: payload.toString() });
});

io.on('connection', (socket) => {
    console.log('linked.');
});

server.listen(3000, () => { 
    console.log('Dashboard online -> http://localhost:3000'); 
});