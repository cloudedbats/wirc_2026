async function setCameraMode(cameraId, cameraMode) {
  try {
    let urlString = '/camera/camera-mode/';
    let params = {
      camera_id: cameraId,
      camera_mode: cameraMode,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setCameraMode: ' + err);
    console.log(err);
  }
}

async function activateRecordTrigger(cameraId) {
  try {
    let urlString = '/camera/record-trigger/';
    let params = {
      cameraId: cameraId,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR activateRecordTrigger: ' + err);
    console.log(err);
  }
}

async function setExposureTime(cameraId, exposureTimeMicroSec) {
  try {
    let urlString =
      '/camera/exposure-time/';
    let params = {
      camera_id: cameraId,
      exposure_time_us: exposureTimeMicroSec,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setExposureTime: ' + err)
    console.log(err)
  }
}

async function setCameraGain(cameraId, cameraGain) {
  try {
    let urlString =
      '/camera/camera-gain/'
    let params = {
      camera_id: cameraId,
      camera_gain: cameraGain,
    };
    await fetch(urlString, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    })
  } catch (err) {
    alert('ERROR setCameraGain: ' + err);
    console.log(err);
  }
}
