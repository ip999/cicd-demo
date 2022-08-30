function sum(a, b) {
    return a + b;
}

function sumHandler(req, res) {
    console.dir(req.body)
    const { a, b } = req.body;
    res.status(200).json(`{ answer: ${sum(a, b)} }`);
}

module.exports = { sumHandler, sum };
