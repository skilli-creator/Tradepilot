let botRunning = false;

// START STATE
export function setBotRunning(state){
  botRunning = state;

  const indicator = document.getElementById("botStatus");

  if(!indicator) return;

  indicator.innerText = state ? "RUNNING" : "STOPPED";
  indicator.style.color = state ? "#22c55e" : "red";
}

// TRADE UPDATE UI
export function addTradeRow(trade){

  const table = document.getElementById("history");

  table.innerHTML += `
    <tr>
      <td>${trade.time}</td>
      <td>${trade.stake}</td>
      <td class="${trade.result > 0 ? 'win' : 'loss'}">
        ${trade.result.toFixed(2)}
      </td>
    </tr>
  `;
}