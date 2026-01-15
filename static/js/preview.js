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

  refreshPreviewStream();
}

function previewModeUpdate() {
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
    fps = 30; // Run on max speed.
  }
  else if (selectedMode == 'preview-10-fps') {
    fps = 10;
  }
  else if (selectedMode == 'preview-5-fps') {
    fps = 5;
  }
  else if (selectedMode == 'preview-2-fps') {
    fps = 2;
  }
  else if (selectedMode == 'preview-1-fps') {
    fps = 1;
  }
  else if (selectedMode == 'preview-0.1-fps') {
    fps = 0.1;
  }
  if (fps != 0) {
    let src_text = 'preview/stream.mjpeg' + '?camera_id=' + selectedCameraId;
    src_text += '&fps=' + fps;
    src_text += '&dummy=' + Math.random(); // To avoid cache.
    image.src = src_text;
  }
}

