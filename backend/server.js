// express api server 
// receives 2 numbers and returns the sum

const express = require('express');
const cors = require('cors');

const PORT = 3000;

const app = express();
app.use(cors());
app.use(express.json());
app.post('/', sum);

function sum(req, res) {
    console.dir(req.body)
    const { a, b } = req.body;
    res.send(`${a} + ${b} = ${a + b}`);
}

app.listen(PORT, () => console.log(`listening on port ${PORT}`));