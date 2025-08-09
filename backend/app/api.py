import os
import httpx
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from . import db, models, schemas, auth

load_dotenv()
router = APIRouter()

TRAIN_API_KEY = os.getenv("TRAIN_API_KEY")
FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY")

# ----- User / data endpoints (simplified) -----
@router.post('/signup', response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db_session: Session = Depends(db.get_db)):
    if payload.email:
        existing = db_session.query(models.User).filter(models.User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail='Email already exists')
    user = models.User(email=payload.email, display_name=payload.display_name)
    if payload.password:
        user.hashed_password = auth.get_password_hash(payload.password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@router.post('/search')
def save_search(payload: schemas.SearchCreate, db_session: Session = Depends(db.get_db)):
    rec = models.SearchHistory(query=payload.query, lat=payload.lat, lng=payload.lng)
    db_session.add(rec)
    db_session.commit()
    db_session.refresh(rec)
    return {'ok': True, 'id': rec.id}

@router.post('/report')
def report(payload: schemas.ReportCreate, db_session: Session = Depends(db.get_db)):
    r = models.RouteReport(type=payload.type, description=payload.description, lat=payload.lat, lng=payload.lng)
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    return {'ok': True, 'id': r.id}

@router.get('/health')
def health():
    return {'ok': True}

# ----- Train connector (IndianRailAPI example) -----
@router.get("/train/status")
async def train_status(train_no: str = Query(...), date: str = Query(...)):
    """
    train_no: train number (string)
    date: DD-MM-YYYY
    Note: replace the endpoint if you're using another train provider.
    """
    if not TRAIN_API_KEY:
        raise HTTPException(status_code=500, detail="TRAIN_API_KEY not set in environment")
    url = f"https://indianrailapi.com/api/v2/livetrainstatus/apikey/{TRAIN_API_KEY}/trainnumber/{train_no}/date/{date}/"
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Train API returned error")
    return resp.json()

# ----- Flight connector (Flightradar24 example) -----
@router.get("/flight/summary")
async def flight_summary(flight_no: str = Query(None), fr24_id: str = Query(None)):
    """
    Example:
      /api/flight/summary?flight_no=AI202
      /api/flight/summary?fr24_id=abcd1234
    NOTE: FR24 may require particular endpoints and tokens. Replace endpoint below with your FR24 contract endpoint.
    """
    if not FLIGHT_API_KEY:
        raise HTTPException(status_code=500, detail="FLIGHT_API_KEY not set in environment")

    # Example public FR24-ish endpoint that returns flights when querying 'query'
    endpoint = "https://fr24api.flightradar24.com/common/v1/flight/list.json"
    headers = {"Authorization": f"Bearer {FLIGHT_API_KEY}"}

    params = {}
    if fr24_id:
        params["flightId"] = fr24_id
    elif flight_no:
        params["query"] = flight_no
    else:
        raise HTTPException(status_code=400, detail="Provide flight_no or fr24_id")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(endpoint, headers=headers, params=params)
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Flight API returned error")
    return resp.json()

# ----- Traffic placeholder -----
@router.get("/traffic/status")
async def traffic_status():
    # Real traffic will be provided via Google Maps/TIles or municipal API; placeholder for now
    return {"message": "Traffic status endpoint placeholder"}
