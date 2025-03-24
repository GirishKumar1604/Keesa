const axios = require('axios');

const predictTransactionType = async (sms) => {
    try {
        console.log(`📡 Sending request to Flask service for SMS: ${sms}`);

        // ✅ Add timeout + better error handling
        const response = await axios.post('http://localhost:5001/predict', 
            { sms }, 
            { timeout: 5000 }
        );

        console.log(`🤖 ML Response: ${JSON.stringify(response.data)}`);
        return response.data.data;
    } catch (err) {
        console.error(`❌ ML prediction failed: ${err.message}`);
        return null;
    }
};

module.exports = { predictTransactionType };
