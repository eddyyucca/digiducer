const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

io.on('connection', (socket) => {
    console.log('a user connected');
    // Kirim data dummy setiap detik
    setInterval(() => {
        socket.emit('data', {
            rmsAcceleration: (Math.random() * 10).toFixed(2),
            velocity: (Math.random() * 10).toFixed(2),
            displacement: (Math.random() * 10).toFixed(2)
        });
    }, 1000);
    socket.on('disconnect', () => {
        console.log('user disconnected');
    });
});

server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});