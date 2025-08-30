var express = require("express"),
  async = require("async"),
  { Pool } = require("pg"),
  cookieParser = require("cookie-parser"),
  app = express(),
  server = require("http").Server(app),
  io = require("socket.io")(server),
  axios = require('axios');

var port = process.env.PORT || 4000;

io.on("connection", function (socket) {
  socket.emit("message", { text: "Welcome! :)" });

  socket.on("subscribe", function (data) {
    socket.join(data.channel);
  });
});

var pool = new Pool({
  connectionString: "postgres://postgres:postgres@db/postgres",
});

async.retry(
  { times: 1000, interval: 1000 },
  function (callback) {
    pool.connect(function (err, client, done) {
      if (err) {
        console.error("Waiting for db");
      }
      callback(err, client);
    });
  },
  function (err, client) {
    if (err) {
      return console.error("Giving up");
    }
    console.log("Connected to db");
    getVotes(client);
  },
);

function getVotes(client) {
  client.query(
    "SELECT id, vote, tweet FROM votes WHERE created_at > NOW() - INTERVAL '10 minutes' ORDER BY created_at DESC",
    [],
    function (err, result) {
      if (err) {
        console.error("Error performing query: " + err);
      } else {
        var votes = collectVotesFromResult(result);
        io.sockets.emit("scores", JSON.stringify(votes));
      }

      setTimeout(function () {
        getVotes(client);
      }, 1000);
    },
  );
}

function collectVotesFromResult(result) {
  return result.rows.map(function(row) {
    return {
      id: row.id,
      tweet: row.tweet,
      vote: row.vote === 'a' ? 'Agree' : 'Disagree'
    };
  });
}

app.use(cookieParser());
app.use(express.urlencoded());
app.use(express.static(__dirname + "/views"));

app.get("/", function (req, res) {
  res.sendFile(path.resolve(__dirname + "/views/index.html"));
});

app.get("/api/analyze", async (req, res) => {
  try {
    const aiAnalyzerService = 'http://ai-analyzer:5001';
    const response = await axios.get(aiAnalyzerService);
    res.send(response.data);
  } catch (error) {
    console.error("Error calling AI analyzer service:", error);
    res.status(500).send("Error calling AI analyzer service");
  }
});

app.get("/health", function (req, res) {
  res.status(200).send("OK");
});

server.listen(port, function () {
  var port = server.address().port;
  console.log("App running on port " + port);
});
