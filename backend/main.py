import keyboard
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from SmileDetector import SmileDetector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load in needed data
    app.state.smileDetector = SmileDetector()
    yield
    # Clean up
    app.state.smileDetector.close()

app = FastAPI(lifespan=lifespan)
# need to use cors to give frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/image")
def get_current_image(request: Request):
    # future work: might be worth using a lock on this data here and above where it is accessed
    return request.app.state.smileDetector.image_data

@app.post("/start_stop")
async def start_stop(request: Request):
    print("start_stop called")
    if request.app.state.smileDetector.currently_capturing:
        request.app.state.smileDetector.stop_detection_thread()
        # else we do nothing and just wait for it to end
        return {"state": "stopped"}
    else:
        request.app.state.smileDetector.start_detection_thread()
        return {"state": "running"}

def local_testing():
    smileDetector = SmileDetector()
    smileDetector.start_detection_thread(True)
    # Need to start primary backend loop (AND stop it when we exit)
    while True:
        if keyboard.read_key() == 'space':
            print('exiting')
            smileDetector.stop_detection_thread()
            break
    smileDetector.close()


if __name__ == "__main__":
    # then we are testing this with no frontend so we run it locally
    local_testing()