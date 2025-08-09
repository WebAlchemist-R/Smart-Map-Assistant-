import uvicorn
import os
import webbrowser
import threading
import time
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from . import api, db, models, ws as wsmod

app = FastAPI(title="RealTimeMaps Backend")

# CORS (open for dev; lock down in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables (prototype)
models.Base.metadata.create_all(bind=db.engine)

app.include_router(api.router, prefix='/api')

# Serve static built frontend if present
FRONTEND_BUILD_PATH = os.getenv('FRONTEND_BUILD_PATH', os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
if os.path.isdir(FRONTEND_BUILD_PATH):
    app.mount('/', StaticFiles(directory=FRONTEND_BUILD_PATH, html=True), name='frontend')
else:
    @app.get('/')
    async def root():
        return {"message": "RealtimeMaps Backend running. Build frontend or run Vite dev server."}

# WebSocket endpoint (simple echo for prototyping)
@app.websocket('/ws/updates')
async def websocket_endpoint(websocket: WebSocket):
    await wsmod.manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        wsmod.manager.disconnect(websocket)

def open_frontend(url: str, delay: float = 1.5):
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url, new=2)
        except Exception:
            print("Could not open browser automatically. Open:", url)
    t = threading.Thread(target=_open, daemon=True)
    t.start()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    dev_url = os.getenv('FRONTEND_DEV_URL', f'http://127.0.0.1:5173')
    # Attempt to open dev URL (Vite) or built site
    open_frontend(dev_url, delay=1.5)
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
