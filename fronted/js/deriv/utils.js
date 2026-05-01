export function formatMoney(value){
  return "$" + Number(value).toFixed(2);
}

export function randomConfidence(){
  return Math.floor(Math.random() * 25 + 70);
}

export function delay(ms){
  return new Promise(resolve => setTimeout(resolve, ms));
}