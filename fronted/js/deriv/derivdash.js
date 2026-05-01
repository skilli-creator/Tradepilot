// ===============================
// TradePilot Bot Engine
// derivdash.js
// ===============================

let mode = "manual";
let stakeMode = "auto";
let running = false;

// Stats
let totalTrades = 0;
let wins = 0;
let losses = 0;
let profit = 0;

// ===============================
// MODE SWITCH
// ===============================
function setMode(selected) {
  mode = selected;

  document.getElementById("manualBox").classList.remove("active");
  document.getElementById("autoBox").classList.remove("active");

  if (selected === "manual") {
    document.getElementById("manualBox").classList.add("active");
    document.getElementById("stakeCard").style.display = "block";
    document.getElementById("autoStakeSection").style.display = "none";
  } else {
    document.getElementById("autoBox").classList.add("active");
    document.getElementById("stakeCard").style.display = "none";
    document.getElementById("autoStakeSection").style.display = "block";
  }
}

// ===============================
// STAKE MODE SWITCH
// ===============================
function setStakeMode(selected) {
  stakeMode = selected;

  document.getElementById("autoStakeBox").classList.remove("active");
  document.getElementById("manualStakeBox").classList.remove("active");

  if (selected === "auto") {
    document.getElementById("autoStakeBox").classList.add("active");
    document.getElementById("manualStakeInput").style.display = "none";
  } else {
    document.getElementById("manualStakeBox").classList.add("active");
    document.getElementById("manualStakeInput").style.display = "block";
  }
}

// ===============================
// BOT START
// ===============================
function startBot() {
  if (running) return;
  running = true;

  // Reset stats
  totalTrades = 0;
  wins = 0;
  losses = 0;
  profit = 0;

  let baseStake = Number(document.getElementById("stake").value) || 10;
  let currentStake = baseStake;

  const takeProfit = Number(document.getElementById("tp").value) || 20;
  const stopLoss = Number(document.getElementById("sl").value) || 10;
  const loopCount = Number(document.getElementById("loops").value) || 10;
  const martingale = document.getElementById("martingale").value;

  const statsBox = document.getElementById("stats");
  const history = document.getElementById("history");

  let interval = setInterval(() => {

    let stake;

    // ===========================
    // STAKE LOGIC
    // ===========================
    if (mode === "automatic") {
      if (stakeMode === "auto") {
        stake = (288.44 * 0.02); // 2% risk
      } else {
        stake = Number(document.getElementById("manualStakeValue").value) || 10;
      }
    } else {
      stake = currentStake;
    }

    // ===========================
    // SIMULATED TRADE RESULT
    // ===========================
    let win = Math.random() > 0.5;
    let result = win ? stake * 0.8 : -stake;

    profit += result;
    totalTrades++;

    if (win) {
      wins++;
      currentStake = baseStake; // reset martingale
    } else {
      losses++;

      // MARTINGALE LOGIC
      if (martingale === "on") {
        currentStake *= 2;

        // safety cap (prevents explosion)
        if (currentStake > baseStake * 8) {
          currentStake = baseStake;
        }
      }
    }

    // ===========================
    // UI UPDATE
    // ===========================
    updateStats(statsBox);
    addHistory(history, stake, win, result);

    // ===========================
    // STOP CONDITIONS
    // ===========================
    if (
      profit >= takeProfit ||
      profit <= -stopLoss ||
      totalTrades >= loopCount
    ) {
      clearInterval(interval);
      running = false;

      statsBox.innerHTML += `<p style="color:yellow;">🛑 BOT STOPPED</p>`;
    }

  }, 1200);
}

// ===============================
// STATS PANEL
// ===============================
function updateStats(box) {
  let winRate = totalTrades > 0 ? ((wins / totalTrades) * 100).toFixed(1) : 0;

  box.innerHTML = `
    <h3>🤖 Bot Status</h3>
    <p>Profit: <b>$${profit.toFixed(2)}</b></p>
    <p>Trades: ${totalTrades}</p>
    <p>Wins: ${wins} | Losses: ${losses}</p>
    <p>Win Rate: ${winRate}%</p>
  `;
}

// ===============================
// HISTORY TABLE
// ===============================
function addHistory(table, stake, win, result) {
  table.innerHTML += `
    <tr>
      <td>${new Date().toLocaleTimeString()}</td>
      <td>$${stake.toFixed(2)}</td>
      <td style="color:${win ? '#22c55e' : '#ef4444'}">
        ${win ? "WIN" : "LOSS"}
      </td>
      <td class="${win ? 'win' : 'loss'}">${result.toFixed(2)}</td>
    </tr>
  `;
}

// ===============================
// LOGOUT
// ===============================
function logout() {
  alert("Logging out...");
  window.location.reload();
}