from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <-- Added Import
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import engine, get_db
from collections import defaultdict
from sqlalchemy import func


# Initialize the FastAPI app
app = FastAPI(
    title="Expense Sharing API",
    description="Backend service to track shared expenses and calculate balances.",
    version="1.0.0"
)

# ==========================
# CORS MIDDLEWARE (THE FIX)
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# ==========================
# USER ENDPOINTS
# ==========================
@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user in the system."""
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Return all users in the system."""
    return crud.get_users(db=db)


# ==========================
# GROUP ENDPOINTS
# ==========================
@app.post("/groups", response_model=schemas.GroupResponse, status_code=201)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    """Create a new group."""
    return crud.create_group(db=db, group=group)

@app.post("/groups/{group_id}/members", status_code=201)
def add_member_to_group(group_id: int, request: schemas.AddMemberRequest, db: Session = Depends(get_db)):
    """Add a user to a specific group."""
    try:
        crud.add_user_to_group(db=db, group_id=group_id, user_id=request.user_id)
        return {"message": f"User {request.user_id} successfully added to group {group_id}."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/groups/{group_id}/members", response_model=list[schemas.UserResponse])
def get_group_members(group_id: int, db: Session = Depends(get_db)):
    """Return all ACTIVE members belonging to a group."""
    members = crud.get_active_group_members(db=db, group_id=group_id)
    return members

# ==========================
# EXPENSE ENDPOINTS
# ==========================
@app.post("/expenses", response_model=schemas.ExpenseResponse, status_code=201)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    """Record a new shared expense."""
    try:
        return crud.create_expense(db=db, expense=expense)
    except ValueError as e:
        # If any of our strict DB validations fail, return a 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/groups/{group_id}/expenses", response_model=list[schemas.ExpenseResponse])
def get_group_expenses(group_id: int, db: Session = Depends(get_db)):
    """Return all expenses for a particular group."""
    return crud.get_group_expenses(db=db, group_id=group_id)


# ==========================
# BALANCE CALCULATION ENDPOINT 
# ==========================
# ==========================
# BALANCE CALCULATION ENDPOINT 
# ==========================
@app.get("/groups/{group_id}/balances")
def get_group_balances(group_id: int, db: Session = Depends(get_db)):
    """
    Calculate consolidated balances for a specific group.
    Uses SQL Aggregation to prevent memory bottlenecks.
    """
    # 1. Verify group exists (The CRUD layer will automatically throw a 404 if it doesn't!)
    crud.get_group(db, group_id)

    # 2. SQL Aggregation
    aggregated_debts = db.query(
        models.ExpenseSplit.user_id.label("debtor_id"),
        models.Expense.paid_by.label("creditor_id"),
        func.sum(models.ExpenseSplit.amount_owed).label("total_debt")
    ).join(
        models.Expense, models.ExpenseSplit.expense_id == models.Expense.id
    ).filter(
        models.Expense.group_id == group_id
    ).group_by(
        models.ExpenseSplit.user_id,
        models.Expense.paid_by
    ).all()

    # Get user names to format the final JSON response
    users = {u.id: u.name for u in crud.get_users(db)}
    
    # 3. Mutual Debt Simplification (Netting the aggregated balances)
    net_balances = defaultdict(lambda: defaultdict(int))
    
    for debtor_id, creditor_id, total_debt in aggregated_debts:
        if debtor_id != creditor_id:
            net_balances[debtor_id][creditor_id] += total_debt
            net_balances[creditor_id][debtor_id] -= total_debt
            
    result = {}
    
    for debtor_id, creditors in net_balances.items():
        debtor_name = users.get(debtor_id, f"User {debtor_id}")
        owes_dict = {}
        
        for creditor_id, net_amount in creditors.items():
            # If the net amount is strictly > 0, they owe money
            if net_amount > 0:
                creditor_name = users.get(creditor_id, f"User {creditor_id}")
                # Convert our safe integer paise back to Rupees for the API
                owes_dict[creditor_name] = net_amount / 100.0 
        
        if owes_dict:
            result[debtor_name] = {"owes": owes_dict}
            
    return result

# ==========================
# DELETE USERS FROM GROUP
# ==========================
@app.delete("/groups/{group_id}/members/{user_id}", status_code=200)
def remove_member_from_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    
    try:
        crud.remove_user_from_group(db=db, group_id=group_id, user_id=user_id)
        return {"message": f"User {user_id} successfully removed from group {group_id}."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
