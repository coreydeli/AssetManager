from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional, List
from enum import Enum

class AssetStatus(str, Enum):
    """
    Mirrors our database AssetStatus enum but as a Pydantic model.
    This ensures consistent status values throughout our application.
    """
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    SOLD = "sold"
    LOST = "lost"

class AssetBase(BaseModel):
    """
    Base schema with fields common to all asset operations.
    This provides the foundation for our asset-related schemas.
    """
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    purchase_price: float = Field(..., gt=0)
    purchase_date: date
    purchase_location: Optional[str] = None
    current_location: Optional[str] = None
    
    # Warranty information
    warranty_cost: Optional[float] = Field(0.0, ge=0)
    warranty_end_date: Optional[date] = None
    warranty_provider: Optional[str] = None
    warranty_terms: Optional[str] = None
    
    # Depreciation settings
    track_depreciation: bool = False
    depreciation_period: Optional[int] = Field(None, gt=0, le=50)  # Maximum 50 years
    
    # Optional identification fields
    serial_number: Optional[str] = None
    barcode: Optional[str] = None

class AssetCreate(AssetBase):
    """
    Schema for creating a new asset. Inherits from AssetBase and adds
    any fields specific to asset creation.
    """
    status: AssetStatus = AssetStatus.ACTIVE
    
    @validator('warranty_end_date')
    def warranty_date_must_be_after_purchase(cls, v, values):
        """
        Ensures that if a warranty end date is provided, it comes after
        the purchase date.
        """
        if v and values.get('purchase_date') and v <= values['purchase_date']:
            raise ValueError('Warranty end date must be after purchase date')
        return v

class AssetUpdate(BaseModel):
    """
    Schema for updating an existing asset. All fields are optional
    since we might want to update only specific fields.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    current_location: Optional[str] = None
    status: Optional[AssetStatus] = None
    warranty_end_date: Optional[date] = None
    warranty_provider: Optional[str] = None
    warranty_terms: Optional[str] = None
    track_depreciation: Optional[bool] = None
    depreciation_period: Optional[int] = Field(None, gt=0, le=50)

class AssetInDB(AssetBase):
    """
    Schema for asset information as it exists in the database.
    Includes all fields plus the database ID.
    """
    id: int
    status: AssetStatus
    image_path: Optional[str] = None
    
    class Config:
        orm_mode = True  # Allows the model to read from ORM objects

class AssetList(BaseModel):
    """
    Schema for returning a list of assets with summary information.
    """
    id: int
    name: str
    purchase_price: float
    current_location: Optional[str]
    status: AssetStatus
    under_warranty: bool
    current_value: float

    class Config:
        orm_mode = True