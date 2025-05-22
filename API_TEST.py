import requests
import json
from settings import YANDEX_API_KEY, UJIN_URL, TOKEN, YANDEX_URL
from fastapi import FastAPI, Request, Header
from typing import Optional

app = FastAPI()


@app.post('/take')
async def take_coords(lst: dict):
    print(lst['coords'])
    return {"status": "success", "received_data": lst}


@app.get('/get')
async def get_coords():
    return {'coords': '123'}


@app.post('/webhook')
async def webhook_handler(request: Request):
    try:
        body = await request.json()
        data = body['ticket']
        title = data['title']
        description = data['description']
        number = data['number']
        priority = data['priority']
        status = data['status']
        sla = data['sla']
        address_str = ''
        # if
        longitude, latitude = get_coordinates_from_address(address_str)
    except Exception:
        pass


def get_first_request():
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "app": "crm",
        "page": 1,
        "per_page": 100,
        'token': 'ust-739706-8f86de46f9cfbaaed65294cd6b0f473c',
        "sort": {},
        "text": "",  # Текст для поиска (опционально)
        "timezone": "Asia/Yekat"
    }
    response = requests.post(UJIN_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']['tickets']
        title = data['title']
        description = data['description']
        number = data['number']
        priority = data['priority']
        status = data['status']
        sla = data['sla']
        address_str = ''
        # if
        longitude, latitude = get_coordinates_from_address(address_str)


def get_coordinates_from_address(address_str: str) -> tuple[float, float] | None:
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": address_str,
        "format": "json",
        "results": 1
    }
    try:
        response = requests.get(YANDEX_URL, params=params)
        response.raise_for_status()
        data = response.json()
        feature_members = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
        if not feature_members:
            return None  # Не найден адрес
        geo_object = feature_members[0].get("GeoObject", {})
        point_str = geo_object.get("Point", {}).get("pos")
        if not point_str:
            return None  # Не найдены координаты
        lon_str, lat_str = point_str.split()
        longitude = float(lon_str)
        latitude = float(lat_str)
        return longitude, latitude
    except Exception:
        return None


if __name__ == '__main__':
    get_first_request()
