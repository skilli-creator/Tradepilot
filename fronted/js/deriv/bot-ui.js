// START BOT
fetch("http://127.0.0.1:5000/api/start", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    mode: "automatic",
    stake: 1
  })
});