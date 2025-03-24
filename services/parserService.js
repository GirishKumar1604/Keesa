const axios = require('axios');

// Define refined regex patterns with improved extraction for date and reference number
const regexPatterns = [
  {
    // General transaction pattern (credits, debits, etc.)
    regex: /(?:rs\.?|inr\.?|₹)?\s*([\d,]+(?:\.\d{2})?)\s+(credited|debited|paid|sent|transferred|refund|failed|balance update)?\s*(?:to|from)?\s*(?:your\s+account(?:\s+ending)?\s+([A-Za-z]*\d{4,})|a\/c\s*x?([A-Za-z]*\d{4,}))?\s*(?:via|by)?\s*(?:for\s+)?([\w\s\-.&]+?)(?=\s+(?:on|at|ref(?:erence)?|txn\s*id|$))\s*(?:(?:on|at)\s+((?:\d{2}\/\d{2}\/\d{4})|(?:\d{2}-[A-Za-z]+-\d{2,4})))?\s*\.?\s*(?:(?:ref(?:erence)?|txn\s*id)[:\s]+([\w\d\-]+))?/i,
    parse: (match) => {
      // Clean up the merchant string: remove a trailing "purchase" if present
      let merchantStr = match[5] ? match[5].trim() : "";
      merchantStr = merchantStr.replace(/\s+purchase\s*$/i, '');
      let merchant = merchantStr || null;
      
      // Date handling: if in DD/MM/YYYY, convert to DD-MM-YYYY; if hyphenated, keep it as is
      let rawDate = match[6] ? match[6].trim() : null;
      let date = null;
      if (rawDate) {
        if (rawDate.match(/\d{2}\/\d{2}\/\d{4}/)) {
          const [day, month, year] = rawDate.split('/');
          date = `${day.padStart(2, '0')}-${month.padStart(2, '0')}-${year}`;
        } else if (rawDate.match(/\d{2}-[A-Za-z]+-\d{2,4}/)) {
          date = rawDate;
        }
      }

      return {
        amount: match[1] ? parseFloat(match[1].replace(/,/g, '')) : null,
        accountNumber: (match[3] || match[4] || null)?.trim(),
        merchant: merchant,
        date: date,
        referenceNumber: match[7] ? match[7].trim() : null
      };
    }
  },
  {
    // Refund-specific pattern with reference detection
    regex: /refund\s+of\s+(?:rs\.?|inr\.?|₹)?\s*([\d,]+(?:\.\d{2})?)\s+(?:processed\s+for\s+order\s+([\d]+))?\s*(?:on|at)\s+((?:\d{2}\/\d{2}\/\d{4})|(?:\d{2}-[A-Za-z]+-\d{2,4}))\s*\.?\s*(?:(?:ref(?:erence)?|txn\s*id)[:\s]+([\w\d\-]+))?/i,
    parse: (match) => {
      let rawDate = match[3] ? match[3].trim() : null;
      let date = null;
      if (rawDate) {
        if (rawDate.match(/\d{2}\/\d{2}\/\d{4}/)) {
          const [day, month, year] = rawDate.split('/');
          date = `${day.padStart(2, '0')}-${month.padStart(2, '0')}-${year}`;
        } else if (rawDate.match(/\d{2}-[A-Za-z]+-\d{2,4}/)) {
          date = rawDate;
        }
      }

      return {
        amount: match[1] ? parseFloat(match[1].replace(/,/g, '')) : null,
        accountNumber: null,  // Not applicable for refund pattern
        merchant: match[2] ? `Order ${match[2]}`.trim() : null,
        date: date,
        referenceNumber: match[4] ? match[4].trim() : null
      };
    }
  }
];

// Main SMS parsing function
const parseSMS = async (sms) => {
  try {
    console.log(`📩 Incoming SMS: "${sms}"`);

    let result = null;

    // Step 1: Try Regex Patterns First
    for (const { regex, parse } of regexPatterns) {
      const match = sms.match(regex);
      console.log(`🧪 Testing Pattern: ${regex}`);
      console.log(`🚨 Match Result: ${JSON.stringify(match)}`);

      if (match) {
        result = parse(match);
        console.log(`✅ Regex Match: ${JSON.stringify(result)}`);
        break;
      }
    }

    // Step 2: ML Fallback if Regex Fails
    if (!result) {
      console.log(`❌ Regex failed — Trying ML prediction...`);
      try {
        const response = await axios.post('http://localhost:5001/predict', { sms });
        const data = response.data;

        result = {
          amount: data?.data?.amount || null,
          accountNumber: data?.data?.account || null,
          merchant: data?.data?.merchant || null,
          date: data?.data?.date || null,
          referenceNumber: data?.data?.referenceNumber || null
        };
        console.log(`🤖 ML Prediction Result: ${JSON.stringify(result)}`);
      } catch (mlError) {
        console.error(`❌ ML Prediction Failed: ${mlError.message}`);
        result = null;
      }
    }

    // Step 3: Clean and Standardize Output (map to required keys)
    if (result) {
      const finalResult = {
        amount: result.amount,
        account: result.accountNumber,
        merchant: result.merchant,
        date: result.date,
        Ref: result.referenceNumber
      };
      console.log(`✅ Final Parsed Result: ${JSON.stringify(finalResult)}`);
      return finalResult;
    } else {
      console.log(`❌ Failed to parse SMS`);
      return null;
    }

  } catch (error) {
    console.error(`❌ Error in parseSMS: ${error.message}`);
    return null;
  }
};

// Export the function
module.exports = { parseSMS };
