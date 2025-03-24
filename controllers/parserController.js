const { parseSMS } = require('../services/parserService');

const parse = async (req, res) => {
    const { sms } = req.body;

    if (!sms) {
        return res.status(400).json({ error: 'No SMS provided' });
    }

    const parsedData = await parseSMS(sms);
    if (!parsedData) {
        return res.status(400).json({ error: 'Failed to parse SMS' });
    }

    res.json({
        success: true,
        data: parsedData
    });
};

module.exports = { parse };
