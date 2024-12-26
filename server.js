const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const usb = require('usb');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

// Temukan perangkat USB Digiducer
const digiducer = usb.findByIds(VENDOR_ID, PRODUCT_ID);

if (digiducer) {
    digiducer.open();
    const interface = digiducer.interfaces[0];
    interface.claim();

    const endpoint = interface.endpoints[0];
    endpoint.startPoll(1, 64);

    endpoint.on('data', (data) => {
        const rmsAcceleration = parseData(data); // Fungsi untuk memproses data
        const velocity = calculateVelocity(rmsAcceleration); // Fungsi untuk menghitung kecepatan
        const displacement = calculateDisplacement(rmsAcceleration); // Fungsi untuk menghitung perpindahan

        io.emit('data', {
            rmsAcceleration,
            velocity,
            displacement
        });
    });

    endpoint.on('error', (err) => {
        console.error('Error:', err);
    });
} else {
    console.error('Digiducer not found');
}

server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});

function parseData(data) {
    // Implementasi parsing data dari sensor
    return (data.readUInt16LE(0) / 100).toFixed(2);
}

function calculateVelocity(rmsAcceleration) {
    // Implementasi perhitungan kecepatan
    return (rmsAcceleration * 0.1).toFixed(2);
}

function calculateDisplacement(rmsAcceleration) {
    // Implementasi perhitungan perpindahan
    return (rmsAcceleration * 0.01).toFixed(2);
}