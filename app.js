const express = require('express');
const bodyParser = require('body-parser');
const connectDB = require('./config/db');

const app = express();

console.log('🚀 Attempting to start server...');

require('dotenv').config();

console.log(`🚀 MONGO_URI = ${process.env.MONGO_URI}`);

// ✅ Middleware
app.use(bodyParser.json());
console.log('✅ Middleware loaded');

// ✅ Connect to MongoDB
connectDB();

// ✅ Define Root Route FIRST to avoid conflicts
app.get('/', (req, res) => {
    console.log('✅ Root route accessed');
    res.send('✅ Server is running...');
});

// ✅ Import and Register Routes
const parserRoutes = require('./routes/parserRoutes');
app.use('/api', parserRoutes);

const PORT = process.env.PORT || 3000;

app.listen(PORT, '127.0.0.1', () => {
    console.log(`✅ Server running on port ${PORT}`);
});
