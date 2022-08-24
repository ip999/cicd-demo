//get verson from package.json
function getVersion() {
    return require('../package.json').version;
}

const sumHandler = require('./sumHandler');
const express = require('express');
const cors = require('cors');

const PORT = 3000;

const app = express();
app.use(cors());
app.use(express.json());
app.post('/', sumHandler);
app.get('/health', readinessHandler);
app.get('/readiness', readinessHandler);
app.get('/version', versionHandler);

function versionHandler(req, res) {
    res.send(getVersion());
}

function readinessHandler(req, res) {
    res.status(200).send("ok");
}

app.listen(PORT, () => console.log(`listening on port ${PORT}`));


