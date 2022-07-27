// express api server 
// receives 2 numbers and returns the sum

//get verson from package.json
function getVersion() {
    return require('../package.json').version;
}

const express = require('express');
const cors = require('cors');

const sumHandler = require('./sumHandler');

const PORT = 3000;

const app = express();
app.use(cors());
app.use(express.json());
app.post('/', sumHandler);
app.get('/readiness', readinessHandler);
app.get('/version', versionHandler);

function versionHandler(req, res) {
    res.status(200).send(getVersion());
}

function readinessHandler(req, res) {
    res.status(200).send("ready");
}

app.listen(PORT, () => console.log(`listening on port ${PORT}`));
