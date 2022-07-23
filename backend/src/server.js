// express api server 
// receives 2 numbers and returns the sum

const express = require('express');
const cors = require('cors');

const sumHandler = require('./sumHandler');

const PORT = 3000;

const app = express();
app.use(cors());
app.use(express.json());
app.post('/', sumHandler);


app.listen(PORT, () => console.log(`listening on port ${PORT}`));


