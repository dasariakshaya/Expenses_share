from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import models
import schemas

# ==========================
# USER CRUD
# ==========================
def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.name == user.name).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail=f"User '{user.name}' already exists."
        )
        
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    
def get_users(db: Session):
    return db.query(models.User).all()
    
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# ==========================
# GROUP CRUD
# ==========================
def create_group(db: Session, group: schemas.GroupCreate):
    existing_group = db.query(models.Group).filter(models.Group.name == group.name).first()
    if existing_group:
        raise HTTPException(
            status_code=400, 
            detail=f"A group named '{group.name}' already exists. Please choose a different name."
        )
        
    db_group = models.Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def get_group(db: Session, group_id: int):
    return db.query(models.Group).filter(models.Group.id == group_id).first()


# ==========================
# GROUP MEMBER CRUD (Upgraded for Soft Deletes)
# ==========================
def add_user_to_group(db: Session, group_id: int, user_id: int):
    # Check if a membership record already exists (even if inactive)
    db_member = db.query(models.GroupMember).filter(
        models.GroupMember.group_id == group_id,
        models.GroupMember.user_id == user_id
    ).first()

    if db_member:
        if db_member.is_active:
            raise ValueError("User is already an active member of this group.")
        # Reactivate a returning user
        db_member.is_active = True
        db_member.left_at = None
    else:
        # Create a completely new membership
        db_member = models.GroupMember(group_id=group_id, user_id=user_id)
        db.add(db_member)
    
    db.commit()
    return db_member

def remove_user_from_group(db: Session, group_id: int, user_id: int):
    db_member = db.query(models.GroupMember).filter(
        models.GroupMember.group_id == group_id,
        models.GroupMember.user_id == user_id,
        models.GroupMember.is_active == True
    ).first()
    
    if not db_member:
        raise ValueError("User is not currently in this group.")
        
    
    db_member.is_active = False
    db_member.left_at = datetime.utcnow()
    db.commit()
    return True

def get_active_group_members(db: Session, group_id: int):
    
    return db.query(models.User).join(models.GroupMember).filter(
        models.GroupMember.group_id == group_id,
        models.GroupMember.is_active == True
    ).all()


# ==========================
# EXPENSE CRUD (Upgraded with Transaction Safety)
# ==========================
def create_expense(db: Session, expense: schemas.ExpenseCreate):
    # 1. Fetch only ACTIVE group members
    active_users = get_active_group_members(db, expense.group_id)
    active_user_ids = [u.id for u in active_users]
    
    if not active_users:
        raise ValueError("Cannot add an expense to an empty group.")
        
    if expense.paid_by not in active_user_ids:
        raise ValueError("The user paying must be an active member of the group.")

    total_paise = int(round(expense.amount * 100))

    # --- TRANSACTION START ---
    try:
        db_expense = models.Expense(
            group_id=expense.group_id,
            paid_by=expense.paid_by,
            amount=total_paise,
            description=expense.description
        )
        db.add(db_expense)
        db.flush() 

        if expense.splits:
            # Check for duplicate user_ids in the custom split payload
            split_user_ids = [split.user_id for split in expense.splits]
            if len(split_user_ids) != len(set(split_user_ids)):
                raise ValueError("Duplicate users found in the custom split.")

            split_paise_amounts = {split.user_id: int(round(split.amount * 100)) for split in expense.splits}
            
            if sum(split_paise_amounts.values()) != total_paise:
                raise ValueError("The sum of custom splits must exactly equal the total expense amount.")
            
            for split in expense.splits:
                if split.user_id not in active_user_ids:
                    raise ValueError(f"User {split.user_id} is not an active member.")
                if split.user_id == expense.paid_by:
                    continue
                    
                db_split = models.ExpenseSplit(
                    expense_id=db_expense.id,
                    user_id=split.user_id,
                    amount_owed=split_paise_amounts[split.user_id]
                )
                db.add(db_split)
        else:
            num_members = len(active_user_ids)
            base_split_amount = total_paise // num_members
            remainder = total_paise % num_members 
            
            for user_id in active_user_ids:
                if user_id == expense.paid_by:
                    continue 
                
                extra_paise = 1 if remainder > 0 else 0
                if extra_paise:
                    remainder -= 1

                db_split = models.ExpenseSplit(
                    expense_id=db_expense.id,
                    user_id=user_id,
                    amount_owed=base_split_amount + extra_paise
                )
                db.add(db_split)

        # If everything above succeeds, lock it into the database permanently
        db.commit()
        db.refresh(db_expense)
        return db_expense
        
    except Exception as e:
        # If ANYTHING fails, wipe the slate clean so we don't store half-written data
        db.rollback()
        raise e
    # --- TRANSACTION END ---

def get_group_expenses(db: Session, group_id: int):
    return db.query(models.Expense).filter(models.Expense.group_id == group_id).all()
