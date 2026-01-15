async function setDetectorTime() {
  try {
    let posixTimeMs = new Date().getTime();
    let urlString = '/system/set-time/?posixtime=' + posixTimeMs;
    await fetch(urlString);
  } catch (err) {
    alert('ERROR setDetectorTime: ' + err);
    console.log(err);
  }
}

async function showDetectorStatus() {
  try {
    let urlString = '/system/detector-status';
    await fetch(urlString);
  } catch (err) {
    alert('ERROR showDetectorStatus: ' + err);
    console.log(err);
  }
}


