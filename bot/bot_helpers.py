import json
from pathlib import Path

import qrcode
from geopy.geocoders import Nominatim

from .constants import DATA_FOLDER


def read_json(filename: str):
    """Десериализовать JSON"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'r', encoding='utf8') as file_:
        file_json = file_.read()
    return json.loads(file_json)


def write_json(data, filename: str):
    """Сериализовать JSON"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'w', encoding='utf8') as file_:
        file_.write(json.dumps(data, indent=4, ensure_ascii=False))


def get_doc(filename: str):
    """Считать и вернуть бинарный файл"""
    with open(Path.cwd() / Path(DATA_FOLDER) / filename,
              'rb') as file_:
        doc = file_.read()
    return doc


def get_location(address: str):
    """Найти адрес по текстовому описанию"""
    geolocator = Nominatim(user_agent="Tester")
    return geolocator.geocode(address)


def generate_qrcode(storage_data: str):
    filename = 'myqr.png'
    qr = qrcode.QRCode(version=1,
                       box_size=10,
                       border=5)
    qr.add_data(storage_data)
    qr.make(fit=True)
    img = qr.make_image()
    file_path = Path.cwd() / Path(DATA_FOLDER) / filename
    img.save(file_path)
    return filename
