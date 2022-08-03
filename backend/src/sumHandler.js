function sumHandler(req, res) {
    console.dir(req.body)
    const { a, b } = req.body;
    res.send(a + b);
}

module.exports = sumHandler;
