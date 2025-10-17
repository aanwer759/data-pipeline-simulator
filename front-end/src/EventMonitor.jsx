import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

// Define the backend URL.
// This will be the same for both Node.js and Rust backends.
const SERVER_URL = 'http://localhost:4000'; 

// Initialize the socket connection outside the component function 
// to prevent it from re-initializing on every render.
const socket = io(SERVER_URL);

function EventMonitor() {
  // State to hold the incoming events
  const [events, setEvents] = useState([]);
  
  // State to hold the connection status
  const [isConnected, setIsConnected] = useState(socket.connected);

  useEffect(() => {
    // --- Socket Connection Handlers ---
    socket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to backend server.');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from backend server.');
    });

    // --- Core Event Listener ---
    // Listen for the 'new_event' broadcast from the server
    socket.on('new_event', (eventData) => {
      // Add the new event to the top of the list
      setEvents(prevEvents => [eventData, ...prevEvents].slice(0, 50)); // Keep only the last 50 events
      
      // OPTIONAL: Emit an event back to the server, e.g., an acknowledgement or a 'client_status' update
      // socket.emit('client_status', { userId: 'user-001', eventCount: prevEvents.length + 1 });
    });

    // Clean up the socket connection on component unmount
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('new_event');
    };
  }, []); // Empty dependency array ensures this runs once on mount

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Real-Time Event Stream Monitor 📈</h1>
      <p>Status: <strong style={{ color: isConnected ? 'green' : 'red' }}>{isConnected ? 'LIVE' : 'DISCONNECTED'}</strong></p>

      <div style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        <h2>Event Log (Last 50)</h2>
        {events.length === 0 ? (
          <p>Waiting for real-time events...</p>
        ) : (
          events.map((event, index) => (
            <div 
              key={index} 
              style={{ 
                borderBottom: '1px dotted #eee', 
                padding: '5px 0', 
                fontSize: '0.9em',
                // Highlight based on event type for visual flair
                color: event.type === 'ALERT' ? 'red' : 'inherit'
              }}
            >
              <span style={{ fontWeight: 'bold' }}>[{new Date(event.timestamp).toLocaleTimeString()}]</span> 
              <span style={{ marginLeft: '10px' }}>Type: {event.type}</span> 
              <span style={{ marginLeft: '10px' }}>ID: {event.id}</span>
              <span style={{ marginLeft: '10px' }}>Value: {event.value.toFixed(2)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default EventMonitor;