const http = require('http');
const PROCESSOR_URL = process.env.PROCESSOR_URL || 'http://localhost:8081/process';
const PORT = 8080;

const server = http.createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/event') {
    res.writeHead(404, {'Content-Type': 'application/json'});
    return res.end(JSON.stringify({error: 'Not found'}));
  }

  let body = '';
  req.on('data', chunk => (body += chunk));
  req.on('end', async () => {
    try {
      const payload = JSON.parse(body);
      const response = await fetch(PROCESSOR_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      res.writeHead(response.status, {'Content-Type': 'application/json'});
      res.end(JSON.stringify(data));
    } catch (err) {
      res.writeHead(500, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({error: err.message}));
    }
  });
});

server.listen(PORT, () => {
  console.log(`Submission Event Function listening on port ${PORT}`);
});
