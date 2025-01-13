from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date
from app.core.database import Base
import enum

class AssetStatus(enum.Enum):
    """
    Tracks the current status of an asset. This helps us manage the asset lifecycle.
    """
    ACTIVE = "active"           
    MAINTENANCE = "maintenance" 
    RETIRED = "retired"        
    SOLD = "sold"             
    LOST = "lost"             

class Asset(Base):
    """
    Main asset model that stores core information about each asset.
    Includes purchase price, warranty details, and depreciation settings
    to give a complete picture of the asset's financial impact.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Purchase and warranty information
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_location = Column(String(255))
    warranty_cost = Column(Float, default=0.0)  # Cost of any extended warranty
    warranty_end_date = Column(Date)  # When the warranty expires
    warranty_provider = Column(String(255))  # Who provides the warranty service
    warranty_terms = Column(Text)  # Description of warranty coverage
    
    # Depreciation settings
    track_depreciation = Column(Boolean, default=False)
    depreciation_period = Column(Integer)
    
    # Rest of the fields remain the same...
    serial_number = Column(String(255), unique=True)
    barcode = Column(String(255), unique=True)
    current_location = Column(String(255))
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    image_path = Column(String(512))
    metadata = Column(JSONB, default={})
    
    # Relationships
    depreciation_records = relationship("DepreciationRecord", back_populates="asset")
    maintenance_records = relationship("MaintenanceRecord", back_populates="asset")

    def get_total_initial_cost(self) -> float:
        """
        Calculates the total initial investment in the asset,
        including both purchase price and warranty cost.
        """
        return self.purchase_price + (self.warranty_cost or 0.0)

    def calculate_current_value(self) -> float:
        """
        Calculates the current value of the asset based on depreciation settings.
        The warranty cost is considered part of the total asset value for depreciation.
        """
        if not self.track_depreciation:
            return self.get_total_initial_cost()
            
        if not self.depreciation_records:
            return self.get_total_initial_cost()
            
        latest_record = max(self.depreciation_records, key=lambda x: x.calculation_date)
        return latest_record.current_value

    def is_under_warranty(self, check_date: date = None) -> bool:
        """
        Determines if the asset is currently under warranty.
        Can also check if it will be under warranty at a future date.
        """
        if not self.warranty_end_date:
            return False
            
        check_date = check_date or date.today()
        return check_date <= self.warranty_end_date

    @classmethod
    async def get_total_asset_value(cls, session) -> dict:
        """
        Calculates the total value of all assets, breaking down:
        - Total purchase costs
        - Total warranty investments
        - Current total value (considering depreciation)
        - Number of assets still under warranty
        """
        assets = await session.query(cls).all()
        
        total_stats = {
            'total_purchase_cost': 0.0,
            'total_warranty_cost': 0.0,
            'total_current_value': 0.0,
            'assets_under_warranty': 0,
            'total_assets': len(assets)
        }
        
        today = date.today()
        
        for asset in assets:
            total_stats['total_purchase_cost'] += asset.purchase_price
            total_stats['total_warranty_cost'] += asset.warranty_cost or 0.0
            total_stats['total_current_value'] += asset.calculate_current_value()
            
            if asset.is_under_warranty(today):
                total_stats['assets_under_warranty'] += 1
        
        return total_stats