export function updateCircle(percent){

  const circle = document.getElementById("circle");

  if(!circle) return;

  circle.style.setProperty("--p", percent + "%");
  circle.innerText = percent + "%";
}

// MANUAL MODE REASONING
export function updateReason(text){

  const box = document.getElementById("reasonBox");
  if(box) box.innerText = text;
}

// MANUAL SIGNAL GENERATOR (UI SIDE ONLY)
export function showManualSignal(data){

  const signalBox = document.getElementById("signal");

  let signal = "";

  if(data.type === "Rise/Fall"){
    signal = data.confidence > 75
      ? "ENTER FALL (3–5 MIN)"
      : "ENTER RISE (3–5 MIN)";
  }

  if(data.type === "Even/Odd"){
    signal = "STATISTICAL EDGE DETECTED";
  }

  signalBox.innerText = signal;
}