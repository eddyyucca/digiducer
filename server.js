const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const usb = require('usb');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Tambahkan Vendor ID dan Product ID
const VENDOR_ID = 0x29DA; // Vendor ID perangkat
const PRODUCT_ID = 0x0007; // Product ID perangkat

// Konfigurasi folder statis dan routing
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

// Temukan perangkat USB Digiducer
const digiducer = usb.findByIds(VENDOR_ID, PRODUCT_ID);

if (digiducer) {
    try {
        digiducer.open();
        const usbInterface = digiducer.interfaces[0];
        usbInterface.claim();

        const endpoint = usbInterface.endpoints[0];
        endpoint.startPoll(1, 64);

        endpoint.on('data', (data) => {
            const rmsAcceleration = parseData(data); // Fungsi untuk memproses data
            const velocity = calculateVelocity(rmsAcceleration); // Fungsi untuk menghitung kecepatan
            const displacement = calculateDisplacement(rmsAcceleration); // Fungsi untuk menghitung perpindahan

            // Emit data ke klien melalui WebSocket
            io.emit('data', {
                rmsAcceleration,
                velocity,
                displacement,
            });
        });

        endpoint.on('error', (err) => {
            console.error('Error:', err);
        });

        console.log('Digiducer device connected.');
    } catch (err) {
        console.error('Error initializing Digiducer:', err);
    }
} else {
    console.error('Digiducer not found.');
}

// Jalankan server
server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});

// Fungsi untuk memproses data dari endpoint
function parseData(data) {
    // Implementasi parsing data dari sensor
    return (data.readUInt16LE(0) / 100).toFixed(2);
}

// Fungsi untuk menghitung kecepatan berdasarkan RMS akselerasi
function calculateVelocity(rmsAcceleration) {
    return (rmsAcceleration * 0.1).toFixed(2);
}

// Fungsi untuk menghitung perpindahan berdasarkan RMS akselerasi
function calculateDisplacement(rmsAcceleration) {
    return (rmsAcceleration * 0.01).toFixed(2);
}
