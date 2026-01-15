var selectedCameraId = 'camera-a';
var selectedCameraName = 'Camera-A';
var cameraStatusAll = {
  'camera-a': {
    'camera_mode': 'camera-off', 'exposure_time_us': 'auto', 'camera_gain': 'auto', 'video_framerate_fps': '30', 'camera_info': 'RPi cam0.'
  },
  'camera-b': {
    'camera_mode': 'camera-off', 'exposure_time_us': 'auto', 'camera_gain': 'auto', 'video_framerate_fps': '30', 'camera_info': 'RPi cam1.'
  },
  'camera-c': {
    'camera_mode': 'camera-off', 'exposure_time_us': 'disabled', 'camera_gain': 'disabled', 'video_framerate_fps': 'disabled', 'camera_info': 'Config id: usb_0.'
  },
  'camera-d': {
    'camera_mode': 'camera-off', 'exposure_time_us': 'disabled', 'camera_gain': 'disabled', 'video_framerate_fps': 'disabled', 'camera_info': 'Config id: usb_1.'
  },
}

function setCameraId(cameraId, cameraName) {
  selectedCameraId = cameraId;
  selectedCameraName = cameraName;
}

function selectCamera(cameraId, cameraName) {
  setCameraId(cameraId, cameraName)

  byId('selectCamAId').classList.remove('is-inverted');
  byId('selectCamBId').classList.remove('is-inverted');
  byId('selectCamCId').classList.remove('is-inverted');
  byId('selectCamDId').classList.remove('is-inverted');
  if (cameraId == 'camera-a') {
    byId('selectCamAId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-b') {
    byId('selectCamBId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-c') {
    byId('selectCamCId').classList.add('is-inverted');
  }
  if (cameraId == 'camera-d') {
    byId('selectCamDId').classList.add('is-inverted');
  }

  // TODO: For test.
  // byId('selectCamCId').disabled = true;
  // byId('selectCamDId').disabled = true;

  byId('cameraTitleId').textContent = selectedCameraName;

  cameraStatusAllUpdate()
  previewModeUpdate();
}

function cameraModeOnChange() {
  let selectedMode =
    byId('cameraModeId').options[byId('cameraModeId').selectedIndex].value;
  if (selectedMode == 'camera-off') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'camera-on') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'record-on') {
    byId('buttonTriggerId').hidden = true;
    setCameraMode(selectedCameraId, selectedMode);
  }
  else if (selectedMode == 'record-on-trigger') {
    byId('buttonTriggerId').hidden = false;
    setCameraMode(selectedCameraId, selectedMode);
  } else {
    alert('Invalid value for cameraModeOnChange: ' + selectedMode + '.');
  }
}

function cameraStatusAllUpdate(cameraStatusAllJson = '') {
  if (cameraStatusAllJson != '') {
    // Use status from Wirc.
    cameraStatusAll = cameraStatusAllJson;
  }
  if (selectedCameraId in cameraStatusAll === true) {
    let status = cameraStatusAll[selectedCameraId];
    if ('camera_mode' in status === true) {
      mode = status['camera_mode']
      byId('cameraModeId').value = mode;
      if (mode === 'record-on-trigger') {
        byId('buttonTriggerId').hidden = false;
      } else {
        byId('buttonTriggerId').hidden = true;
      }
    }
    if ('exposure_time_us' in status === true) {
      exposure = status['exposure_time_us']
      if (exposure === 'disabled') {
        byId('exposureTimeId').disabled = true;
        byId('exposureTimeId').value = 'auto';
      } else {
        byId('exposureTimeId').disabled = false;
        byId('exposureTimeId').value = exposure;
      }
    }
    if ('camera_gain' in status === true) {
      gain = status['camera_gain']
      if (gain === 'disabled') {
        byId('cameraGainId').disabled = true;
        byId('cameraGainId').value = 'auto';
      } else {
        byId('cameraGainId').disabled = false;
        byId('cameraGainId').value = gain;
      }
    }
    if ('camera_info' in status === true) {
      info = status['camera_info']
      byId('cameraInfoId').textContent = info;
    }
  }
}

function recordTriggerClicked() {
  activateRecordTrigger(selectedCameraId);
}

function cameraSettingsOnChange() {

}

function cameraSettingsUpdate() {

}

function exposureTimeOnChange() {
  let selectedValue =
    byId('exposureTimeId').options[byId('exposureTimeId').selectedIndex].value
  setExposureTime(selectedCameraId, selectedValue)
}

function cameraGainOnChange() {
  let selectedValue =
    byId('cameraGainId').options[byId('cameraGainId').selectedIndex].value
  setCameraGain(selectedCameraId, selectedValue)
}
