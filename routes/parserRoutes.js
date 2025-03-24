const express = require('express');
const router = express.Router();
const { parseSMS } = require('../services/parserService'); // ✅ Fixed Import Path
const { predictTransactionType } = require('../services/mlService');

router.post('/parse-sms', async (req, res) => {
    const { sms } = req.body;

    if (!sms) {
        console.error('❌ No SMS provided');
        return res.status(400).json({ error: 'No SMS provided' });
    }

    console.log(`📩 Received SMS: ${sms}`);

    let parsedData = null;

    try {
        // ✅ Step 1: Try Regex Parsing First
        parsedData = await parseSMS(sms);
        console.log(`🧪 Regex Result: ${JSON.stringify(parsedData)}`);
    } catch (regexError) {
        console.error(`❌ Regex Parsing Failed: ${regexError.message}`);
    }

    // ✅ Step 2: ML Fallback if Regex Fails
    if (!parsedData || !parsedData.merchant || !parsedData.transactionType) {
        console.log('❌ Regex failed — Trying ML prediction...');
        try {
            const mlData = await predictTransactionType(sms);
            if (mlData) {
                parsedData = {
                    amount: mlData.amount || parsedData?.amount || null,
                    transactionType: mlData.transactionType || parsedData?.transactionType || "unknown",
                    merchant: mlData.merchant || parsedData?.merchant || "Unknown",
                    referenceNumber: mlData.referenceNumber || parsedData?.referenceNumber || null,
                    fraudFlags: mlData.fraudFlags || parsedData?.fraudFlags || []
                };
            }
            console.log(`🤖 ML Prediction Result: ${JSON.stringify(parsedData)}`);
        } catch (mlError) {
            console.error(`❌ ML Prediction Failed: ${mlError.message}`);
        }
    }

    if (!parsedData) {
        console.error('❌ Failed to parse SMS');
        return res.status(400).json({ error: 'Failed to parse SMS' });
    }

    console.log(`✅ Final Parsed Data: ${JSON.stringify(parsedData)}`);

    // ✅ Step 3: Return Structured Response
    return res.json({
        success: true,
        data: parsedData
    });
});

module.exports = router;
