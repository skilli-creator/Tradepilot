// ===============================
// TradePilot REAL Bot Dashboard
// ===============================

let running = false;
let poller = null;

// ===============================
// START BOT (REAL BACKEND)
// ===============================
function startBot() {
  if (running) return;

  const token = document.getElementById("token").value;

  if (!token) {
    alert("Please enter your Deriv API Token");
    return;
  }

  const config = {
    stake: document.getElementById("stake").value,
    tp: document.getElementById("tp").value,
    sl: document.getElementById("sl").value,
    loops: document.getElementById("loops").value,
    martingale: document.getElementById("martingale").value,
    tradeType: document.getElementById("tradeType").value,
    market: document.getElementById("market").value,
    token: token
  };

  fetch("http://localhost:5000/start-bot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(config)
  })
    .then(res => res.json())
    .then(data => {
      console.log(data);
      running = true;
      startPolling();
    })
    .catch(err => console.error(err));
}

// ===============================
// STOP BOT
// ===============================
function stopBot() {
  fetch("http://localhost:5000/stop-bot", {
    method: "POST"
  });

  running = false;

  if (poller) clearInterval(poller);
}

// ===============================
// POLL BACKEND STATUS (LIVE)
// ===============================
function startPolling() {

  const statsBox = document.getElementById("stats");

  poller = setInterval(() => {

    fetch("http://localhost:5000/bot-status")
      .then(res => res.json())
      .then(data => {

        updateStats(statsBox, data);
        updateLiveInfo(data);

        if (!data.running) {
          clearInterval(poller);
          running = false;
        }
      })
      .catch(err => console.error(err));

  }, 1000);
}

// ===============================
// UPDATE UI (REAL DATA)
// ===============================
function updateStats(box, data) {

  box.innerHTML = `
    <h3>🤖 Bot Status</h3>

    <p>Running: <b>${data.running ? "YES" : "NO"}</b></p>

    <p>Profit: <b>$${data.profit}</b></p>
    <p>Balance: <b>$${data.balance}</b></p>

    <p>Trades: ${data.trades}</p>
    <p>Wins: ${data.wins} | Losses: ${data.losses}</p>
    <p>Win Rate: ${data.win_rate}%</p>

    <p>Current Stake: $${data.current_stake}</p>

    <p>Last Result:
      <span style="color:${data.last_result === 'win' ? '#22c55e' : '#ef4444'}">
        ${data.last_result || "-"}
      </span>
    </p>

    <hr/>

    <p><b>AI Confidence:</b> ${data.confidence}%</p>
    <p><b>Reason:</b> ${data.reasoning}</p>
  `;
}

// ===============================
// LIVE TRADE FEED
// ===============================
function updateLiveInfo(data) {

  const history = document.getElementById("history");

  if (!data.last_result) return;

  const color = data.last_result === "win" ? "#22c55e" : "#ef4444";

  history.innerHTML += `
    <tr>
      <td>${new Date().toLocaleTimeString()}</td>
      <td>$${data.current_stake}</td>
      <td style="color:${color}">
        ${data.last_result.toUpperCase()}
      </td>
      <td>${data.profit}</td>
    </tr>
  `;

  // auto-scroll
  history.scrollTop = history.scrollHeight;
}

// ===============================
// LOGOUT
// ===============================
function logout() {
  stopBot();
  alert("Logged out");
  window.location.reload();
}