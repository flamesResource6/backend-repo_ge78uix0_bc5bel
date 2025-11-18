import os
from typing import List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Appointment, GalleryImage, User, Product

app = FastAPI(title="Drone Services API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_doc(doc: dict) -> dict:
    out = {**doc}
    if "_id" in out and isinstance(out["_id"], ObjectId):
        out["id"] = str(out.pop("_id"))
    # Convert datetimes to isoformat strings
    for k, v in list(out.items()):
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
    return out


@app.get("/")
def read_root():
    return {"message": "Drone Services Backend is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Drone Services API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Env checks
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ----- Appointment Endpoints -----

class AppointmentResponse(BaseModel):
    id: str
    message: str


@app.post("/api/appointments", response_model=AppointmentResponse)
def create_appointment(appt: Appointment):
    try:
        inserted_id = create_document("appointment", appt)
        return {"id": inserted_id, "message": "Appointment request received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointments", response_model=List[dict])
def list_appointments():
    try:
        docs = get_documents("appointment")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Gallery Endpoints -----

DEFAULT_GALLERY: List[dict] = [
    {
        "url": "https://images.unsplash.com/photo-1504194104404-433180773017?q=80&w=1200&auto=format&fit=crop",
        "title": "Coastal Cliffs",
        "category": "Nature",
    },
    {
        "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200&auto=format&fit=crop",
        "title": "Mountain Range",
        "category": "Landscapes",
    },
    {
        "url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
        "title": "City From Above",
        "category": "Real Estate",
    },
    {
        "url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1200&auto=format&fit=crop",
        "title": "Golden Fields",
        "category": "Agriculture",
    },
]


@app.get("/api/gallery")
def get_gallery():
    try:
        stored = get_documents("galleryimage")
        stored_serialized = [serialize_doc(d) for d in stored]
        if not stored_serialized:
            # Provide default showcase if none in DB yet
            return {"items": DEFAULT_GALLERY, "count": len(DEFAULT_GALLERY), "source": "default"}
        return {"items": stored_serialized, "count": len(stored_serialized), "source": "database"}
    except Exception:
        # If database not configured, still return defaults so frontend works
        return {"items": DEFAULT_GALLERY, "count": len(DEFAULT_GALLERY), "source": "default"}


@app.post("/api/gallery")
def add_gallery_image(img: GalleryImage):
    try:
        inserted_id = create_document("galleryimage", img)
        return {"id": inserted_id, "message": "Image added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Schema Endpoint (optional helper) -----

@app.get("/schema")
def get_schema():
    return {
        "schemas": {
            "user": User.model_json_schema(),
            "product": Product.model_json_schema(),
            "appointment": Appointment.model_json_schema(),
            "galleryimage": GalleryImage.model_json_schema(),
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
