from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Alice"])

class UserResponse(UserCreate):
    id: int = Field(..., gt=0, examples=[1])
    created_at: datetime

    class Config:
        from_attributes = True

# --- GROUP SCHEMAS ---
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Weekend Trip"])

class GroupResponse(GroupCreate):
    id: int = Field(..., gt=0, examples=[1])
    created_at: datetime

    class Config:
        from_attributes = True

# --- EXPENSE SCHEMAS ---
class ExpenseSplitCreate(BaseModel):
    user_id: int = Field(..., gt=0, examples=[2])
    amount: float = Field(..., gt=0, examples=[500.50])

class ExpenseCreate(BaseModel):
    group_id: int = Field(..., gt=0, examples=[1])
    paid_by: int = Field(..., gt=0, examples=[1])
    amount: float = Field(..., gt=0, examples=[1500.00])
    description: str = Field(..., min_length=1, examples=["Dinner at Joey's"])
    splits: Optional[List[ExpenseSplitCreate]] = None

class ExpenseResponse(BaseModel):
    id: int = Field(..., gt=0, examples=[100])
    group_id: int = Field(..., gt=0, examples=[1])
    paid_by: int = Field(..., gt=0, examples=[1])
    amount: float = Field(..., gt=0, examples=[1500.00])
    description: str = Field(..., examples=["Dinner at Joey's"])
    created_at: datetime

    class Config:
        from_attributes = True
