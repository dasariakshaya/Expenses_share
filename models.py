from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # UPGRADE: Unique constraint prevents duplicate identical accounts
    name = Column(String, unique=True, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", secondary="group_members", back_populates="members")
    expenses_paid = relationship("Expense", back_populates="payer")
    expense_splits = relationship("ExpenseSplit", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", secondary="group_members", back_populates="groups")
    expenses = relationship("Expense", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    # UPGRADE: Added a primary key ID so a user can join, leave, and rejoin later
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    
    # UPGRADE: Soft Delete functionality
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    paid_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    amount = Column(Integer, nullable=False) 
    description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    amount_owed = Column(Integer, nullable=False)

    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")