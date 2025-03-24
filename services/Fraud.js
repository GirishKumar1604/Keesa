const fraudKeywords = [
    'OTP', 'suspicious', 'unauthorized', 'blocked', 'fraud', 
    'risk', 'unauthenticated', 'transaction blocked', 'hacked'
];

const detectFraud = (sms) => {
    for (const keyword of fraudKeywords) {
        if (sms.toLowerCase().includes(keyword.toLowerCase())) {
            return true;
        }
    }
    return false;
};

module.exports = detectFraud;
