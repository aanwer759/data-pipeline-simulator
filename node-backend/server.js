const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
// Create an HTTP server instance from the Express app
const server = http.createServer(app);
const PORT = 4000; // Must match the SERVER_URL in your React frontend

// --- Middleware Setup ---
// Enable CORS for the frontend (React app will be on a different port, e.g., 3000 or 5173)
app.use(cors({
    origin: 'http://localhost:8080', // Update this if your React app uses a different port
    methods: ['GET', 'POST']
}));
/*
// --- Socket.io Setup ---
// Attach Socket.io to the HTTP server
const io = new Server(server, {
    cors: {
        origin: 'http://localhost:8080', // Must match React app origin
        methods: ['GET', 'POST']
    }
});
*/
// A simple counter to generate unique IDs for events
let eventCounter = 1000;

// --- Event Generation Logic ---
// Function to generate a random event object
const generateEvent = () => {
    const types = ['SENSOR_READING', 'USER_ACTIVITY', 'ALERT', 'SYSTEM_INFO'];
    const randomType = types[Math.floor(Math.random() * types.length)];

    eventCounter++;
    
    return {
        id: eventCounter,
        type: randomType,
        // Simulate a value fluctuation
        value: Math.random() * 100, 
        timestamp: new Date().toISOString()
    };
};

// --- Socket.io Connection & Real-Time Emitter ---
io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}. Total connected: ${io.engine.clientsCount}`);

    // Optional: Log any custom events emitted by the client (e.g., acknowledged messages)
    socket.on('client_status', (data) => {
        // You would typically log this to MongoDB or process it here.
        // For now, we'll just log to the console.
        console.log(`Client ${socket.id} status update:`, data);
    });

    socket.on('disconnect', () => {
        console.log(`Client disconnected: ${socket.id}. Total connected: ${io.engine.clientsCount}`);
    });
});

// Start the real-time event generator that broadcasts to ALL connected clients
// We use setInterval outside the 'connection' handler so only one timer runs for all clients.
setInterval(() => {
    const eventData = generateEvent();
    
    // Broadcast the event to all connected sockets on the 'new_event' channel
    io.emit('new_event', eventData); 
    
    // console.log(`Emitted event ${eventData.id}: ${eventData.type}`); // Uncomment for heavy logging
}, 500); // Emit a new event every 500 milliseconds (0.5 seconds)


// --- Express HTTP Route (Optional) ---
app.get('/', (req, res) => {
    res.send('Event Stream Backend is running. Establish a WebSocket connection to start receiving data.');
});

// --- Start Server ---
server.listen(PORT, () => {
    console.log(`Node.js/Socket.io Server is listening on port ${PORT}`);
    console.log(`Connecting your React app to http://localhost:${PORT}`);
});