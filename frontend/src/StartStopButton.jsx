import React, { useState } from "react";
export function StartStopButton() {
  const [cameraState, setcameraState] = useState("stopped");

  function StartCapture() {
    fetch("http://localhost:8000/start_stop", { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        console.log(data.state);
        setcameraState(data.state);
      })
      .catch((err) => console.error("failed to set camera state, err"));
  }

  return (
    <div
      style={{ display: "flex", justifyContent: "right", alignItems: "center" }}
    >
      <button type="button" onClick={StartCapture}>
        {cameraState === "running" ? "Stop capture" : "Start capture"}
      </button>
      {cameraState}
    </div>
  );
}
