executeWithTimeout = (handler) => async (req, res, next) => {
    const timer = setTimeout(() => {
        res.status(408).send({ error: 'Request timeout' });
    }, 3000);

    try {
        await handler(req, res);
    } catch (error) {
        next(error);
    } finally {
        clearTimeout(timer);
    }
};

module.exports = executeWithTimeout;
