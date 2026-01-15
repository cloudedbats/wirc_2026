let wsDisconnectedCounter = 0;

// Generic function.
function byId(id) {
  return document.getElementById(id);
}

function hideModules() {
  byId('heroBodyCameraId').hidden = true;
  byId('heroBodyAboutId').hidden = true;
}

function activateModuleCamera() {
  hideModules();
  byId('heroBodyCameraId').hidden = false;
}

function toggleModuleAbout() {
  if (byId('heroBodyAboutId').hidden) {
    byId('heroBodyCameraId').hidden = true;
    byId('heroBodyAboutId').hidden = false;
  } else {
    byId('heroBodyCameraId').hidden = false;
    byId('heroBodyAboutId').hidden = true;
  }
}

function fetchModuleCamera() {
  hideModules();
  try {
    fetch('/pages/camera', {
      method: 'GET',
    })
      .then(function (response) {
        if (response.ok) {
          return response.text();
        } else {
          return Promise.reject(response);
        }
      })
      .then(function (html) {
        byId('heroBodyCameraId').innerHTML = html;
        activateModuleCamera();
      })
      .catch(function (err) {
        console.warn('Error in fetchModuleCamera: ', err)
      })
    // selectCamera(selectedCameraId, selectedCameraName)
  } catch (err) {
    alert('ERROR fetchModuleAbout: ' + err)
    console.log(err)
  }
}

function fetchModuleAbout() {
  hideModules();
  try {
    fetch('/pages/about', {
      method: 'GET',
    })
      .then(function (response) {
        if (response.ok) {
          return response.text();
        } else {
          return Promise.reject(response);
        }
      })
      .then(function (html) {
        byId('heroBodyAboutId').innerHTML = html;
      })
      .catch(function (err) {
        console.warn('Error in fetchModuleAbout: ', err);
      })
  } catch (err) {
    alert('ERROR fetchModuleAbout: ' + err);
    console.log(err);
  }
}

// Startup. Called from body onLoad.
function fetchModules() {
  setTimeout(fetchAllModules, 500);
}

function fetchAllModules() {
  fetchModuleCamera();
  fetchModuleAbout();
  activateModuleCamera();
  setTimeout(loadWebsocket, 1000);
}

function loadWebsocket() {
  var ws_url = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  ws_url += window.location.host; // Note: Host includes port.
  ws_url += '/system/websocket';
  startWebsocket(ws_url);
}

function startWebsocket(wsUrl) {
  // let ws = new WebSocket('ws://localhost:8082/ws');
  let ws = new WebSocket(wsUrl);
  ws.onmessage = function (event) {
    let dataJson = JSON.parse(event.data);
    if ('status' in dataJson === true) {
      updateStatus(dataJson.status);
    }
    if ('logRows' in dataJson === true) {
      updateLogTable(dataJson.logRows);
    }
    if ('cameraStatusAll' in dataJson === true) {
      cameraStatusAllUpdate(dataJson.cameraStatusAll);
    }

    // if ('cam0_exposure_time_us' in dataJson === true) {
    //   updateExposureTime(dataJson.cam0_exposure_time_us, dataJson.cam1_exposure_time_us);
    // }
    // if ('cam0_camera_gain' in dataJson === true) {
    //   updateCameraGain(dataJson.cam0_camera_gain, dataJson.cam1_camera_gain);
    // }

    // if ('cam0_streaming_started' in dataJson === true) {
    //   if (selectedCameraId == 'camera-a') {
    //     refreshPreviewStream();
    //   }
    // }
    // if ('cam1_streaming_started' in dataJson === true) {
    //   if (selectedCameraId == 'camera-b') {
    //     refreshPreviewStream();
    //   }
    // }
  }
  ws.onclose = function (event) {
    // Try to reconnect in 5th seconds.
    ws = null
    updateDisconnectedInfo();
    setTimeout(function () {
      startWebsocket(wsUrl)
    }, 5000);
  }
  ws.onerror = function (event) {
    // updateDisconnectedInfo();
  }
}

function updateDisconnectedInfo() {
  let waitText = 'DISCONNECTED';
  if (wsDisconnectedCounter == 0) {
    waitText = 'DISCONNECTED.';;
  } else if (wsDisconnectedCounter == 1) {
    waitText = 'DISCONNECTED..';
  } else if (wsDisconnectedCounter == 2) {
    waitText = 'DISCONNECTED...';
  }
  wsDisconnectedCounter += 1;
  if (wsDisconnectedCounter >= 3) {
    wsDisconnectedCounter = 0;
  }
  let statusWhenDisconnected = {
    detectorTime: waitText
  }
  updateStatus(statusWhenDisconnected);
}
