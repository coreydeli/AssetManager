from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate, AssetList
import logging

logger = logging.getLogger(__name__)

class AssetService:
    """
    Service layer for handling asset-related operations.
    This separates our business logic from our API routes and database models.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_asset(self, asset_data: AssetCreate) -> Asset:
        """
        Creates a new asset in the system. This method handles the creation process,
        including any necessary validation or business logic.
        """
        try:
            # Create new asset instance from our validated data
            asset = Asset(**asset_data.dict())
            
            # Add and commit to database
            self.db.add(asset)
            await self.db.commit()
            await self.db.refresh(asset)
            
            logger.info(f"Created new asset: {asset.name} (ID: {asset.id})")
            return asset
            
        except Exception as e:
            logger.error(f"Error creating asset: {str(e)}")
            await self.db.rollback()
            raise

    async def get_asset(self, asset_id: int) -> Optional[Asset]:
        """
        Retrieves a single asset by its ID, including related depreciation
        and maintenance records.
        """
        query = select(Asset).where(Asset.id == asset_id).options(
            selectinload(Asset.depreciation_records),
            selectinload(Asset.maintenance_records)
        )
        result = await self.db.execute(query)
        asset = result.scalar_one_or_none()
        
        if asset:
            logger.debug(f"Retrieved asset: {asset.name} (ID: {asset.id})")
        else:
            logger.debug(f"No asset found with ID: {asset_id}")
            
        return asset

    async def list_assets(
        self,
        skip: int = 0,
        limit: int = 100,
        location: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Asset]:
        """
        Retrieves a list of assets with optional filtering and pagination.
        This helps manage large asset collections efficiently.
        """
        # Build our query based on filters
        query = select(Asset)
        
        if location:
            query = query.filter(Asset.current_location == location)
        if status:
            query = query.filter(Asset.status == status)
            
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        assets = result.scalars().all()
        
        logger.info(f"Retrieved {len(assets)} assets")
        return assets

    async def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> Optional[Asset]:
        """
        Updates an existing asset with new data. Only updates the fields
        that are provided in the update data.
        """
        try:
            # First check if asset exists
            asset = await self.get_asset(asset_id)
            if not asset:
                logger.warning(f"Attempted to update non-existent asset ID: {asset_id}")
                return None

            # Update only the fields that were provided
            update_data = asset_data.dict(exclude_unset=True)
            
            # Perform the update
            query = (
                update(Asset)
                .where(Asset.id == asset_id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )
            await self.db.execute(query)
            await self.db.commit()
            
            # Refresh and return the updated asset
            await self.db.refresh(asset)
            logger.info(f"Updated asset: {asset.name} (ID: {asset.id})")
            return asset
            
        except Exception as e:
            logger.error(f"Error updating asset {asset_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def delete_asset(self, asset_id: int) -> bool:
        """
        Removes an asset from the system. This is a soft delete that marks
        the asset as RETIRED rather than actually deleting it.
        """
        try:
            asset = await self.get_asset(asset_id)
            if not asset:
                return False
                
            # Perform soft delete by updating status
            asset.status = "RETIRED"
            await self.db.commit()
            
            logger.info(f"Soft deleted asset: {asset.name} (ID: {asset.id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def get_total_asset_value(self) -> dict:
        """
        Calculates the total value of all active assets in the system.
        Provides a financial overview of the asset portfolio.
        """
        query = select(Asset).where(Asset.status == "ACTIVE")
        result = await self.db.execute(query)
        assets = result.scalars().all()
        
        total_stats = {
            'total_purchase_value': sum(asset.purchase_price for asset in assets),
            'total_warranty_value': sum(asset.warranty_cost or 0 for asset in assets),
            'total_current_value': sum(asset.calculate_current_value() for asset in assets),
            'asset_count': len(assets)
        }
        
        logger.info("Calculated total asset values")
        return total_stats