const API_BASE = "http://127.0.0.1:5000";

// START BOT
export async function startBot(payload) {
  const res = await fetch(`${API_BASE}/start-bot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  return await res.json();
}

// STOP BOT
export async function stopBot() {
  const res = await fetch(`${API_BASE}/stop-bot`, {
    method: "POST"
  });

  return await res.json();
}

// GET STATUS
export async function getStatus() {
  const res = await fetch(`${API_BASE}/bot-status`);
  return await res.json();
}

// GET ACCOUNT INFO
export async function getAccount() {
  const res = await fetch(`${API_BASE}/account`);
  return await res.json();
}