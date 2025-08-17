"""Workflow API endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_workflows():
    return {"message": "Workflows endpoint"}