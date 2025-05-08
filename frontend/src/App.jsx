import React, { useEffect, useState } from "react";
import { StartStopButton } from "./StartStopButton";

function App() {
  const [image, setImage] = useState([]);
  const [smileCoordinates, setSmileCoordinates] = useState([]);

  useEffect(() => {
    const fetchImage = () => {
      fetch("http://localhost:8000/image")
        .then((res) => res.json())
        .then((data) => {
          setImage(data.image);
          setSmileCoordinates(data.coordinates);
        })
        .catch((err) => console.error("Error fetching image:", err));
    };

    const interval = setInterval(fetchImage, 20);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div style={{ width: "60%", float: "left" }}>
        <img src={image} />
      </div>
      <div style={{ width: "40%", float: "right" }}>
        <StartStopButton />
        <h1>{smileCoordinates}</h1>
      </div>
    </>
  );
}

export default App;
