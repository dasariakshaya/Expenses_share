from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime

# ==========================
# USER SCHEMAS
# ==========================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Alice"])

class UserResponse(BaseModel):
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==========================
# GROUP SCHEMAS
# ==========================
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Weekend Trip"])

class GroupResponse(BaseModel):
    id: str = Field(..., examples=["987e6543-e21b-34d3-b456-426614174111"])
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AddMemberRequest(BaseModel):
    user_id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])

# ==========================
# EXPENSE SCHEMAS
# ==========================
class SplitInput(BaseModel):
    user_id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    amount: float = Field(..., gt=0, examples=[500.00]) 

class ExpenseCreate(BaseModel):
    group_id: str = Field(..., examples=["987e6543-e21b-34d3-b456-426614174111"])
    paid_by: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    amount: int = Field(..., gt=0, examples=[150000]) # Represents paise for precision
    description: str = Field(..., min_length=1, examples=["Dinner at Joey's"])
    
    splits: Optional[List[SplitInput]] = Field(
        default=None, 
        examples=[[
            {"user_id": "123e4567-e89b-12d3-a456-426614174000", "amount": 75000},
            {"user_id": "abc12345-e89b-12d3-a456-426614174999", "amount": 75000}
        ]]
    )

class ExpenseResponse(BaseModel):
    id: str = Field(..., examples=["expense-uuid-here"])
    group_id: str 
    paid_by: str 
    amount: float
    description: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator('amount', mode='before')
    @classmethod
    def convert_to_rupees(cls, v):
        if isinstance(v, int):
             return v / 100.0
        return v
