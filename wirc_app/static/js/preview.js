// Preview mode is stored on client only.
var selectedPreviewMode = {
  'camera-a': 'preview-off',
  'camera-b': 'preview-off',
  'camera-c': 'preview-off',
  'camera-d': 'preview-off',
}

function previewModeOnChange() {
  let previewModeId = byId('previewModeId');
  let selectedMode =
    previewModeId.options[previewModeId.selectedIndex].value;
  selectedPreviewMode[selectedCameraId] = selectedMode;

  cameraModeOnChange();

  refreshPreviewStream();
}

function previewModeUpdate() {
  // Turn preview off if camera is off.
  if (selectedCameraId in cameraStatusAll === true) {
    let status = cameraStatusAll[selectedCameraId];
    if ('preview_mode' in status === true) {
      let preview_mode = status['preview_mode'];
      if (preview_mode == 'preview-off') {
        selectedPreviewMode[selectedCameraId] = 'preview-off';
      }
    }
  }
  // Change selected value.
  let selectedMode = selectedPreviewMode[selectedCameraId];
  byId('previewModeId').value = selectedMode;

  refreshPreviewStream();
}

async function refreshPreviewStream() {
  let image = byId('mjpegStreamId');
  image.removeAttribute('src');

  let selectedMode = selectedPreviewMode[selectedCameraId];
  let fps = 0; // 0 = OFF.
  if (selectedMode == 'preview-on') {
    fps = 10;
  }
  else if (selectedMode == 'fullsize-10fps') {
    fps = 10;
  }
  else if (selectedMode == 'preview-5fps') {
    fps = 5;
  }
  else if (selectedMode == 'preview-2fps') {
    fps = 2;
  }
  else if (selectedMode == 'preview-1fps') {
    fps = 1;
  }
  if (fps != 0) {
    let src_text = 'preview/stream.mjpeg' + '?camera_id=' + selectedCameraId;
    src_text += '&fps=' + fps;
    src_text += '&dummy=' + Math.random(); // To avoid cache.
    image.src = src_text;
  }
}

