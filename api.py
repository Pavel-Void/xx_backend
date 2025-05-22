from fastapi import FastAPI

app = FastAPI()


@app.post('/take')
async def take_coords(lst: dict):
    print(lst['coords'])
    return {"status": "success", "received_data": lst}


@app.get('/get')
async def gege_coords():
    return {'coords': '123'}
