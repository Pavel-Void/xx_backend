from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/postBounds")
async def take_coords(request: Request):
    data = await request.json()
    try:
        print(f"Координаты: {data}")
        return {
            "status": "success",
            "received_data": data
        }

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )




@app.get('/api/getBounds')
async def gege_coords():
    return {'coords': '123'}
