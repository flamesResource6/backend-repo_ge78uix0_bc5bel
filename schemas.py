"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Drone services app schemas

class Appointment(BaseModel):
    """
    Appointment requests from prospects
    Collection name: "appointment"
    """
    name: str = Field(..., description="Client full name", min_length=2)
    email: EmailStr = Field(..., description="Client email")
    phone: str = Field(..., description="Contact phone number", min_length=7)
    service: str = Field(..., description="Requested service (e.g., Real Estate, Events, Inspections)")
    preferred_date: str = Field(..., description="Preferred date (ISO date string)")
    message: Optional[str] = Field(None, description="Additional details or notes")
    source: str = Field("website", description="Lead source")

class GalleryImage(BaseModel):
    """
    Portfolio gallery images
    Collection name: "galleryimage"
    """
    url: str = Field(..., description="Public image URL")
    title: Optional[str] = Field(None, description="Short title/caption")
    category: Optional[str] = Field(None, description="Category or tag")
    taken_at: Optional[datetime] = Field(None, description="When the photo/video was captured")
