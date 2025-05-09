
import sqlite3
import sqlalchemy
import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
import cv2


class Base(DeclarativeBase):
    pass

class Smile(Base):
    __tablename__ = 'smiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    disk_location: Mapped[str]
    x: Mapped[int]
    y: Mapped[int]
    w: Mapped[int]
    h: Mapped[int]
    time: Mapped[datetime.datetime]

def __repr__(self):
    return f"<Smile(id={self.id}, location='{self.disk_location}', x={self.x}, y={self.y}, w={self.w}, h={self.h}, time={self.time})>"

class LocalDBConnection:

    def __init__(self):
        con = sqlite3.connect('smileInformation.db') # this will create the local database whether it exists already or not
        con.close()
        self.engine = sqlalchemy.create_engine('sqlite:///smileInformation.db', echo=True)
        Base.metadata.create_all(self.engine)

    def add_smiles(self, smiles, full_image):
        if len(smiles) == 0:
            return
        [curr_datetime, file_locations] = self.save_smile_data(smiles, full_image)
        smiles_to_store = []
        for i in range(len(smiles)):
            smiles_to_store.append(Smile(
                disk_location=file_locations[i],
                x = int(smiles[i][0]),
                y = int(smiles[i][1]),
                w = int(smiles[i][2]),
                h = int(smiles[i][3]),
                time = curr_datetime
            ))
        with Session(self.engine) as session:
            session.add_all(smiles_to_store)
            session.commit()

    def save_smile_data(self, smiles, image):
        # the smiles are saved in subfolder 'smile images' rather than directly into the database
        smile_num = 1
        curr_time = datetime.datetime.now()
        file_locations = []
        for (x, y, w, h) in smiles:
            smile_img = image[y:y + h, x:x + w]
            filename = f'smile images\\{curr_time}_{smile_num}.png'
            file_locations.append(filename)
            cv2.imwrite(filename.replace(':', '_').replace('-', '_'), smile_img)
            smile_num += 1
        return curr_time, file_locations

    def close(self):
        self.engine.dispose()

