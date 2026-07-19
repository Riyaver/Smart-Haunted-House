const express = require('express');
const mqtt = require('mqtt');
const { Server } = require('socket.io');
const http = require('http');
const path = require('path');

MQTT_PORT = 8883
MQTT_BROKER = "157cc16c2b0443d0931cfacc745a094f.s1.eu.hivemq.cloud"
MQTT_USER = "SHH"
MQTT_PASSWORD = "grp16_shh"

const mqttOptions = {
    port: 8883,
    username: MQTT_USER,
    password: MQTT_PASSWORD,
    rejectUnauthorized: false
};

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

const mqttClient = mqtt.connect(`mqtts://${MQTT_BROKER}`, mqttOptions);

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