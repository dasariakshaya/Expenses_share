# Decentro: Shared Expense Tracker API

A production-grade RESTful API built with **FastAPI** and **PostgreSQL** to manage group expenses, custom splitting logic, and mutual debt simplification.

---

## 🚀 Engineering Highlights

This application goes beyond basic CRUD operations by implementing several enterprise-grade architectural patterns:

* **O(n) SQL Aggregation:** The `GET /balances` endpoint offloads mathematical heavy lifting to the database. Instead of pulling entire transaction histories into Python memory (which causes O(n) scaling bottlenecks), it uses PostgreSQL `GROUP BY` and `SUM()` functions to return a single netted matrix.

* **Soft-Delete Architecture:** Users are not hard-deleted from groups. The `GroupMembers` ledger utilizes `is_active` flags and `left_at` timestamps. This ensures a user can leave a group without destroying the immutability of historical financial calculations.

* **ACID Transaction Safety:** The custom expense-splitting logic is wrapped in strict database transaction blocks (`db.rollback()`). If a custom split payload contains mathematical errors or missing users, the entire database transaction is safely aborted, preventing orphaned debts.

* **Containerized Environment:** Fully Dockerized with dynamic database routing. The app seamlessly switches between a local SQLite file for rapid prototyping and an enterprise PostgreSQL container for production deployment.

---

## 🛠 Tech Stack

* **Framework:** FastAPI (Python 3.11)
* **Database:** PostgreSQL (Production) / SQLite (Local)
* **ORM:** SQLAlchemy 2.0 + Pydantic v2
* **Containerization:** Docker & Docker Compose
* **Frontend Testing:** Vanilla JavaScript + Fetch API (Included `index.html` thin client)

---

## 🐳 Quick Start (Docker)

### 1. Clone the Repository

```bash
git clone <https://github.com/dasariakshaya/Expenses_share.git>
cd Expenses_share
```

### 2. Build and Start Containers

```bash
docker-compose up --build
```

### 3. Open Swagger Documentation

Navigate to:

```text
http://localhost:8000/docs
```

### 4. Test Using the Frontend

Open the included `index.html` file in your browser while the backend server is running.

---

## 📖 Core API Reference

### Users & Groups

#### Create User

```http
POST /users
```

#### Create Group

```http
POST /groups
```

#### Add Member to Group

```http
POST /groups/{group_id}/members
```

#### Get Group Members

```http
GET /groups/{group_id}/members
```

#### Remove Member (Soft Delete)

```http
DELETE /groups/{group_id}/members/{user_id}
```

---

### Expenses & Ledger

#### Create Expense

Supports:

* Equal Split (default)
* Custom Split (manual)

```http
POST /expenses
```

#### Get Group Expenses

```http
GET /groups/{group_id}/expenses
```

#### Get Simplified Balances

```http
GET /groups/{group_id}/balances
```

Returns the final netted debts between users after all expenses are aggregated and simplified.

---

## 🧪 Testing Custom Splits

To test unequal expense sharing, send the following payload to:

```http
POST /expenses
```

### Request Body

```json
{
  "group_id": 1,
  "paid_by": 1,
  "amount": 1200,
  "description": "Dinner with custom split",
  "splits": [
    {
      "user_id": 2,
      "amount": 800
    },
    {
      "user_id": 3,
      "amount": 400
    }
  ]
}
```

### Validation Rules

The backend validates:

1. All users exist.
2. All users belong to the specified group.
3. Split amounts are positive.
4. Total split amount equals expense amount.
5. Duplicate users are rejected.
6. Transaction rolls back if validation fails.

---

## 📂 Project Structure

```text
.
## 📁 Folder Structure

Expenses_share/
├── main.py              # FastAPI application instance and API route definitions
├── models.py            # SQLAlchemy database models (Table schemas)
├── schemas.py           # Pydantic models for request/response validation
├── crud.py              # Core database logic and queries
├── database.py          # Database connection, engine, and session management
├── index.html           # Thin client testing dashboard (Vanilla JS/Bootstrap)
├── Dockerfile           # Instructions to containerize the FastAPI app
├── docker-compose.yml   # Orchestration for the API and PostgreSQL containers
└── requirements.txt     # Python package dependencies
```
## 🗄️ Database Schema Explanation

The PostgreSQL database is normalized into 5 core tables to ensure strict data integrity and support complex ledger querying:

1. **`users`**: Stores core user identity. Enforces unique constraints to prevent duplicate accounts.
2. **`groups`**: Stores group metadata.
3. **`group_members`**: A relational mapping table linking users to groups. **Crucial Feature:** It utilizes `is_active` and `left_at` columns to support "soft deletes." This preserves the immutable history of past expenses even if a user leaves a group.
4. **`expenses`**: The master record for a transaction. It tracks the `group_id`, the `paid_by` user, and the total transaction amount (stored securely as integer paise to prevent floating-point math errors).
5. **`expense_splits`**: The granular ledger. It permanently records the exact fractional debt owed by each participant for a specific expense. This table structure allows the system to seamlessly support both algorithmic Equal Splits and manual Custom Splits without altering the core schema.
