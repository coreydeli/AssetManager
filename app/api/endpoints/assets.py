from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.asset_service import AssetService
from app.schemas.asset import AssetCreate, AssetUpdate, AssetInDB, AssetList
import logging

logger = logging.getLogger(__name__)

# Create router for asset endpoints
router = APIRouter(prefix="/assets", tags=["assets"])

@router.post("/", response_model=AssetInDB)
async def create_asset(
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new asset in the system"""
    service = AssetService(db)
    try:
        asset = await service.create_asset(asset_data)
        return asset
    except Exception as e:
        logger.error(f"Error creating asset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{asset_id}", response_model=AssetInDB)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a specific asset by ID"""
    service = AssetService(db)
    asset = await service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.get("/", response_model=List[AssetList])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    location: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List assets with optional filtering and pagination"""
    service = AssetService(db)
    assets = await service.list_assets(skip, limit, location, status)
    return assets

@router.patch("/{asset_id}", response_model=AssetInDB)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing asset"""
    service = AssetService(db)
    asset = await service.update_asset(asset_id, asset_data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete an asset"""
    service = AssetService(db)
    success = await service.delete_asset(asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset successfully deleted"}

@router.get("/summary/values")
async def get_asset_values(
    db: AsyncSession = Depends(get_db)
):
    """Get summary of total asset values"""
    service = AssetService(db)
    return await service.get_total_asset_value()