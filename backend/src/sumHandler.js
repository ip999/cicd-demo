function sumHandler(req, res) {
    console.dir(req.body)
    const { a, b } = req.body;
    res.status(200).json(`{ answer: ${a + b} }`);
}

module.exports = sumHandler;
