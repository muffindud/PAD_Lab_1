var jwt = require('jsonwebtoken');

generateUserToken = (username) => {
    return jwt.sign({
        username: username
    }, process.env.JWT_USER_SECRET, {
        expiresIn: 86400 // 24 hours
    });
}

verifyUserToken = (token) => {
    return jwt.verify(token, process.env.JWT_USER_SECRET);
}

verifyInternalToken = (token) => {
    return jwt.verify(token, process.env.JWT_INTERNAL_SECRET);
}

module.exports = {
    generateUserToken,
    verifyUserToken,
    // generateInternalToken,
    verifyInternalToken
}
