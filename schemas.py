from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from pydantic import field_validator

# ==========================
# USER SCHEMAS
# ==========================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the user")

class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    # THE FIX: This replaces the old 'class Config:'
    model_config = ConfigDict(from_attributes=True)


# ==========================
# GROUP SCHEMAS
# ==========================
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the group")

class GroupResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    # THE FIX: This replaces the old 'class Config:'
    model_config = ConfigDict(from_attributes=True)

class AddMemberRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user to add")


 

# ==========================
# EXPENSE SCHEMAS
# ==========================
class SplitInput(BaseModel):
    """Used for the bonus feature: Custom Unequal Splits"""
    user_id: int
    amount: float = Field(..., gt=0, description="Amount owed in Rupees") # Changed to float

class ExpenseCreate(BaseModel):
    group_id: int
    paid_by: int
    amount: float = Field(..., gt=0, description="Total expense amount in Rupees") # Changed to float
    description: str = Field(..., min_length=1)
    
    splits: Optional[List[SplitInput]] = None 

class ExpenseResponse(BaseModel):
    id: int
    group_id: int
    paid_by: int
    amount: float # Changed to float
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # THE MAGIC TRICK: When reading from the database, divide the integer by 100 to output Rupees
    @field_validator('amount', mode='before')
    def convert_to_rupees(cls, v):
        return v / 100.0
    
# ==========================
# BALANCE SCHEMAS
# ==========================
class OweDetail(BaseModel):
    owes: dict[str, int]