# 💸 Shared Expense Tracker API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge\&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge\&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge\&logo=docker)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)

A production-grade RESTful API built to manage group expenses, handle complex custom splitting logic, and calculate simplified mutual debts.

---

## 🚀 Engineering Highlights

This application goes beyond basic CRUD operations by implementing several enterprise-grade architectural patterns:

* **Enterprise Security (UUIDs):** Completely abandoned sequential integer IDs in favor of UUIDv4 strings across the entire database to prevent data-scraping and ensure unguessable API endpoints.

* **O(n) SQL Aggregation:** The `GET /balances` endpoint offloads mathematical heavy lifting to PostgreSQL. Instead of loading entire transaction histories into Python memory, it uses database-side aggregation with `GROUP BY` and `SUM()` functions.

* **ACID Transaction Safety:** Custom expense-splitting logic is wrapped inside strict transaction blocks. If any validation fails, the entire operation is rolled back to prevent orphaned or inconsistent financial records.

* **Soft Delete Architecture:** Users are never permanently removed from groups. The `group_members` ledger uses `is_active` flags and `left_at` timestamps to preserve historical financial integrity.

* **Containerized Environment:** Fully Dockerized API and PostgreSQL deployment for reproducible development and production environments.

---

## 🛠 Tech Stack

| Layer             | Technology                     |
| ----------------- | ------------------------------ |
| Framework         | FastAPI (Python 3.11)          |
| Database          | PostgreSQL                     |
| ORM               | SQLAlchemy 2.0                 |
| Validation        | Pydantic v2                    |
| Containerization  | Docker & Docker Compose        |
| Frontend Testing  | Vanilla JavaScript + Fetch API |
| API Documentation | Swagger UI / OpenAPI           |

---

# 🐳 Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/dasariakshaya/Expenses_share.git
cd Expenses_share
```

## 2. Build and Start Containers

```bash
docker-compose up --build
```

## 3. Access Swagger Documentation

Open your browser and navigate to:

```text
http://localhost:8000/docs
```

---

## 4. Using the Testing Dashboard

This repository includes a lightweight frontend dashboard (`index.html`) for quickly testing API functionality.

### Features

* Zero configuration setup
* Runs directly in the browser
* Automatically detects local/cloud deployment environments
* Uses Fetch API for communication

Simply open:

```text
index.html
```

in your browser.

---

# 💰 Expense Splitting Engine

The system supports both automatic equal splits and custom unequal splits.

---

## Scenario A: Automatic Equal Split

When the `splits` field is omitted, the backend automatically retrieves all active members in the group and divides the expense equally.

### Request

```http
POST /expenses
```

```json
{
  "group_id": "987e6543-e21b-34d3-b456-426614174111",
  "paid_by": "123e4567-e89b-12d3-a456-426614174000",
  "amount": 150000,
  "description": "Dinner (Auto Split)"
}
```

### Notes

Amounts are stored as integer paise/cents rather than floating-point values to eliminate rounding errors.

---

## Scenario B: Custom Unequal Split

Provide a custom `splits` array when different participants owe different amounts.

### Request

```http
POST /expenses
```

```json
{
  "group_id": "987e6543-e21b-34d3-b456-426614174111",
  "paid_by": "123e4567-e89b-12d3-a456-426614174000",
  "amount": 120000,
  "description": "Dinner with Custom Split",
  "splits": [
    {
      "user_id": "abc12345-e89b-12d3-a456-426614174999",
      "amount": 80000
    },
    {
      "user_id": "xyz98765-e89b-12d3-a456-426614174888",
      "amount": 40000
    }
  ]
}
```

---

# ✅ Validation Rules

Before saving an expense, the API validates:

* User exists.
* User belongs to the specified group.
* User is active in the group.
* Split amounts are greater than zero.
* Total split amount exactly matches expense amount.
* Duplicate users are rejected.
* Invalid UUIDs are rejected.

If any validation fails:

```http
HTTP 400 Bad Request
```

The database transaction is rolled back automatically.

---

# 📂 Project Structure

```text
Expenses_share/
│
├── main.py
├── crud.py
├── models.py
├── schemas.py
├── database.py
│
├── index.html
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
└── README.md
```

### File Responsibilities

| File                 | Purpose                                  |
| -------------------- | ---------------------------------------- |
| `main.py`            | API routes and FastAPI initialization    |
| `crud.py`            | Database business logic                  |
| `models.py`          | SQLAlchemy models                        |
| `schemas.py`         | Pydantic request/response schemas        |
| `database.py`        | Database connection and session handling |
| `index.html`         | Lightweight API testing client           |
| `Dockerfile`         | FastAPI container configuration          |
| `docker-compose.yml` | PostgreSQL + API orchestration           |

---

# 🗄 Database Schema Architecture

The database follows a normalized ledger-based design.

## users

Stores user information.

### Fields

```text
id (UUID)
name
email
created_at
```

### Constraints

* UUID Primary Key
* Unique Email

---

## groups

Stores group metadata.

### Fields

```text
id (UUID)
name
created_at
```

---

## group_members

Relationship table connecting users and groups.

### Fields

```text
group_id
user_id
is_active
joined_at
left_at
```

### Special Feature

Supports soft deletion without affecting historical financial calculations.

---

## expenses

Master transaction records.

### Fields

```text
id
group_id
paid_by
amount
description
created_at
```

---

## expense_splits

Stores exact debt obligations generated from each expense.

### Fields

```text
expense_id
user_id
amount
```

This table enables:

* Equal splitting
* Custom splitting
* Historical auditing
* Debt simplification

without changing the schema.

---

# 📊 Balance Calculation Strategy

Instead of iterating through every expense in Python:

```python
for expense in expenses:
    ...
```

the API performs aggregation directly in PostgreSQL:

```sql
SELECT
    debtor_id,
    creditor_id,
    SUM(amount)
FROM expense_splits
GROUP BY debtor_id, creditor_id;
```

Benefits:

* Lower memory usage
* Faster response times
* Better scalability
* Database-optimized execution plans

---

# 🔒 Security Considerations

### UUID-Based Resources

```text
/users/{uuid}
/groups/{uuid}
/expenses/{uuid}
```

Prevent predictable endpoint enumeration.

### Input Validation

Implemented through:

* FastAPI
* Pydantic
* SQLAlchemy Constraints

### Transaction Safety

All multi-table writes are wrapped in atomic transactions.

---

# 📈 Future Improvements

* JWT Authentication
* Role-Based Access Control (RBAC)
* Expense Categories
* Recurring Expenses
* Settlement APIs
* Audit Logs
* Multi-Currency Support
* Redis Caching
* Kubernetes Deployment
* CI/CD Pipeline

---

# 🧪 Example API Flow

### Create User

```http
POST /users
```

### Create Group

```http
POST /groups
```

### Add Members

```http
POST /groups/{group_id}/members
```

### Add Expense

```http
POST /expenses
```

### View Balances

```http
GET /balances/{group_id}
```

---


GitHub:
https://github.com/dasariakshaya
