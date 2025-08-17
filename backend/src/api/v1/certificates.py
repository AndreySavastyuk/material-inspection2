"""Certificates API endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_certificates():
    return {"message": "Certificates endpoint"}