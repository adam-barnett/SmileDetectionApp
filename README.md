# SmileDetectionApp
small app using Python backend and react frontend to detect and display smiles

# Setup and use
required:
- react with vite
- Python3 with (opencv-python, keyboard, fastapi, uvicorn, sqlalchemy.  All can be installed with pip)
- local camera

Tools I used:
- vscode for react with 'prettier' extension 
- pycharm for Python
- Chrome with React Developer Tools extension
- DB Browser 

Getting it running:
- from a terminal in the backend folder `run uvicorn main:app --reload`
- from a terminal in the frontend folder run `npm run dev` (may require running `npm install` first)
- open the frontend in your provided browser using the link provided (likely http://localhost:5173/)

Alternatively to test the backend on its own, run the backend main.py in python

Common issues:
- if you have multiple vite react programs running the address may not be http://localhost:5173/ (likely it will be 5174 or higher), in this case the backend will need to be updated to this new origin by changing the app.add_middleware 'allow_origins' option to include this new address [NOTE - it is possible to give this a much more permissive setup where it will allow any origins, for now I felt it was better to proceed with a more limited input]

Future work:
- Improvements to the UI. (adding style and better controlled alignment of the GUI elements would clearly be beneficial)
- Automated tests on both ends (currently only basic user driven testing exists for the backend and none for the frontend, I'd like to add automated testing to both pieces)
- Provide some data at the frontend. (in addition to the coordinates of the smiles, it would be nice to have an updating graph which plots the smile positions recorded so far in this session)
- Provide more options and control from the frontend. (some useful additions are a way to choose the framerate of display, which camera to connect to, to reference old data, and to see the individual smiles (and mark them as correct or not for future learning))
- Improve detection. (currently the detection uses haarcascades with fairly arbitrarily chosen inputs, some optimisation of these would be good (perhaps ultimately with some dynamic optimisation of those options to the specific lighting situation of the current camera))
- Convert the backend to be a remote server. (Currently this is built in such a way that the backend must be running on the local machine, as it is the thing collecting frames. Switching to having the camera connection be at the frontend would allow this to be something that I could potentially host online with the backend being run on a server I set up myself)

Sources used:
https://mk.bcgsc.ca/colorblind/palettes.mhtml (colorblind friendly color references)
https://docs.sqlalchemy.org/en/20/orm/quickstart.html (for an overview of sqlalchemy)

