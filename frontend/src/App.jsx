import React, { useEffect, useState } from "react";
import { StartStopBotton } from "./StartStopButton";

function App() {
  const [image, setImage] = useState([]);

  useEffect(() => {
    const fetchImage = () => {
      fetch("http://localhost:8000/image")
        .then((res) => res.json())
        .then((data) => setImage(data))
        .catch((err) => console.error("Error fetching image:", err));
    };

    const interval = setInterval(fetchImage, 20); // Refresh every 20 milliseconds (future work: make this value and option to be set)

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <div>
      <img src={image} />
      <StartStopBotton />
    </div>
  );
}

export default App;
