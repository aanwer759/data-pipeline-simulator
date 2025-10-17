const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const redis = require('redis');
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

// --- Socket.io Setup ---
// Attach Socket.io to the HTTP server
const io = new Server(server, {
    cors: {
        origin: 'http://localhost:8080', // Must match React app origin
        methods: ['GET', 'POST']
    }
});

const client = redis.createClient({
    // Using a Promise-based client is the modern standard for async/await
    legacyMode: false 
});

client.on('error', (err) => console.log('Redis Client Error', err));

async function connectToRedis() {
    try {
        await client.connect();
        console.log('Successfully connected to Redis!');
    } catch (err) {
        console.error('Could not connect to Redis:', err);
    }
}

/**
 * Iteratively retrieves all keys matching a pattern using the SCAN command.
 * @param {string} pattern - The glob-style pattern (e.g., 'user:*').
 * @returns {Promise<string[]>} - A promise that resolves to an array of matching keys.
 */
async function getKeysByScan(pattern) {
    let cursor = '0'; // The starting cursor for the iteration
    let keys = [];
    
    // The SCAN command syntax: SCAN cursor [MATCH pattern] [COUNT count]
    // The response is an array: [new_cursor, [key1, key2, ...]]
    do {
        // Use a reasonable COUNT (e.g., 1000) for balance
        //const reply = await client.scan(cursor, { MATCH: pattern, COUNT: 1000 });
        const reply = await client.scan(cursor, {MATCH: "device1_data*"});
        // Update the cursor for the next iteration
        cursor = parseInt(reply.cursor, 10); 
        
        // Add the retrieved keys to the array
        keys = keys.concat(reply.keys);
        
    } while (cursor !== 0); // The iteration finishes when the cursor returns to '0'

    return keys;
}

connectToRedis();

async function readStringData(key) {
    try {
        const pattern = 'device1_data:';
        const matchingKeys = await getKeysByScan(pattern);
        //const matchingKeys = await getKeysByScan(pattern);
        
        console.log(`Found ${matchingKeys.length} keys matching '${pattern}':`);
        // Now you have the list of keys, you can use MGET, HMGET, etc., to fetch their data.
        console.log(matchingKeys);
        
        // Example: Retrieve the data for all found keys (assuming they are simple strings)
        if (matchingKeys.length > 0) {
            const data = await client.mGet(matchingKeys);
            console.log("\nData for these keys (MGET):", data);
        }
        
    } catch (error) {
        console.error("An error occurred during SCAN operation:", error);
    }
}

// Example: Retrieve a simple event counter value
//readStringData('event_counter_id');

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
setInterval(async () => {
    try{
        eventData = await readStringData('device1_data:device-1_0_2');
    // Broadcast the event to all connected sockets on the 'new_event' channel
    if (eventData){
    console.log("before sending data to frontend");
    console.log(eventData);
    io.emit('new_event', eventData); 
    
    }

    }
    catch(error){
        console.log(error)
    }
        // console.log(`Emitted event ${eventData.id}: ${eventData.type}`); // Uncomment for heavy logging
}, 500); // Emit a new event every 500 milliseconds (0.5 seconds)


// --- Express HTTP Route (Optional) ---
app.get('/', (req, res) => {
    res.send('Event Stream Backend is running. Establish a WebSocket connection to start receiving data.');
});

app.get("/device-1", (req, res) => {
    res.send("this page should contain socket for device 1 stream")
});

// --- Start Server ---
server.listen(PORT, () => {
    console.log(`Node.js/Socket.io Server is listening on port ${PORT}`);
    console.log(`Connecting your React app to http://localhost:${PORT}`);
});