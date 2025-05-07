export function StartStopBotton() {
  return (
    // <Button
    //   onPress={StartCapture}
    //   title="Start Capture"
    //   color="#841584"
    //   accessibilityLabel="Start capture of video and detecting of smiles"
    // />
    <button type="button" onClick={StartCapture}>
      Start Capture
    </button>
  );
}

function StartCapture() {
  fetch("http://localhost:8000/start_stop", { method: "POST" });
}
