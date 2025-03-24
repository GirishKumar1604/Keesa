const patterns = [
    // ✅ General Pattern for Credit/Debit/UPI/NEFT/IMPS/Refund/Failed
    /(?:rs\.?|inr\.?)?\s*([\d,]+\.\d{2})\s+(credited|debited|refund|balance update)?\s+(?:to|from)?\s*(?:a\/c\s*x?(\d{4,}))?\s*(?:on|at)?\s*((\d{2}\/\d{2}\/\d{4})|(\d{2}-[A-Za-z0-9]+-\d{2,4}))?\s*(?:via|by)?\s*([\w\s]+)?\s*(?:ref|txn\s*id)?\s*([\w\d]+)/i,

    // ✅ Pattern for Failed Transactions
    /(?:rs\.?|inr\.?)?\s*([\d,]+\.\d{2})\s+(credited|debited|refund)?\s+(?:to|from)?\s*(?:a\/c\s*x?(\d{4,}))?\s*failed\s*(?:ref|txn\s*id)?\s*([\w\d]+)/i,

    // ✅ Pattern for Wallet Transactions
    /(?:rs\.?|inr\.?)?\s*([\d,]+\.\d{2})\s+(credited|debited|refund)?\s+(?:to|from)?\s*(?:wallet)?\s*(?:ref|txn\s*id)?\s*([\w\d]+)/i
];

const parseSMS = (sms) => {
    console.log(`📩 Incoming SMS: ${sms}`);
    
    for (const pattern of patterns) {
        console.log(`🧪 Testing Pattern: ${pattern}`);
        const match = sms.match(pattern);
        console.log(`🚨 Match Result: ${match}`);

        if (match) {
            console.log(`✅ Regex Matched: ${JSON.stringify(match)}`);
            return {
                amount: match[1] ? parseFloat(match[1].replace(/,/g, '')) : null,
                transactionType: match[2] ? match[2].toLowerCase() : null,
                accountNumber: match[3] || null,
                date: match[4] || null,
                bankName: match[7] || null,
                referenceNumber: match[8] || null
            };
        }
    }
    console.error('❌ No regex pattern matched');
    return null;
};

// ✅ Export parseSMS correctly
module.exports = { parseSMS };
