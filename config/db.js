const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        console.log(`🚀 Attempting MongoDB connection: ${process.env.MONGO_URI}`);
        await mongoose.connect(process.env.MONGO_URI);
        console.log('✅ MongoDB connected');
    } catch (err) {
        console.error('❌ MongoDB connection error:', err.message);
        process.exit(1); // Stop the server if DB connection fails
    }
};

module.exports = connectDB;
