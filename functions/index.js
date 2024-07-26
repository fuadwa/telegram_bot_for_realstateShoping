const functions = require("firebase-functions");
const {spawn} = require("child_process");

exports.telegramBot = functions.https.onRequest((req, res) => {
  const process = spawn("python", ["bot.py"]);
  let response = "";

  process.stdout.on("data", (data) => {
    response += data.toString();
  });

  process.stderr.on("data", (data) => {
    console.error(data.toString());
  });

  process.on("close", (code) => {
    res.status(200).send(response);
  });
});
