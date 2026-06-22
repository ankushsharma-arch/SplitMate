# SplitMate

SplitMate is a small Django REST API for group expense splitting and debt settlement. It is designed as a hands-on coding interview exercise: candidates explore the codebase, reproduce QA-reported issues, and fix them with minimal, clean changes.

---

## About

Groups of people use SplitMate to:

- Create expense groups and invite members
- Add shared expenses with equal or custom splits per member
- Support multi-currency expenses within a single INR group
- Record manual settlements between members
- Calculate the minimum set of transactions to clear all debts

**Tech stack:** Python 3.11+, Django 5, Django REST Framework, SQLite — no frontend or external services required.

**Expense flow:** Group created → Members added → Expenses logged → Splits calculated → Settlements recorded → Balances resolved

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/ankushsharma-arch/SplitMate.git
cd splitmate
```

### 2. Create a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Run the development server

```bash
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

### 6. (Optional) Django admin

```bash
python manage.py createsuperuser
```

Then open `http://127.0.0.1:8000/admin/`

---

## Domain Models

| Model          | Description                                                  |
|----------------|--------------------------------------------------------------|
| `Group`        | A shared expense group with a base currency and member list  |
| `User`         | Django built-in user; acts as group member and expense payer |
| `Expense`      | A shared cost logged against a group with a payer            |
| `ExpenseSplit` | A single member's share of an expense                        |
| `Payment`      | A manual settlement recorded between two group members       |

---

## API Endpoints

| Method    | Endpoint                                     | Description                                     |
|-----------|----------------------------------------------|-------------------------------------------------|
| GET/POST  | `/api/groups/`                               | List your groups or create a new one            |
| GET/PUT   | `/api/groups/{id}/`                          | Retrieve or update a group                      |
| POST/DEL  | `/api/groups/{id}/members/`                  | Add or remove members                           |
| GET       | `/api/groups/{id}/balances/`                 | Net balances for all members in a group         |
| POST      | `/api/expenses/`                             | Add a new expense to a group                    |
| GET       | `/api/expenses/group/{group_id}/`            | List all expenses in a group                    |
| GET/PUT   | `/api/expenses/{id}/`                        | Retrieve or update a specific expense           |
| GET       | `/api/expenses/group/{group_id}/settle-up/`  | Minimum transactions to clear all debts         |
| POST      | `/api/payments/`                             | Record a manual settlement between two members  |
| GET       | `/api/payments/group/{group_id}/`            | List all payments within a group                |
| GET       | `/api/payments/group/{group_id}/summary/`    | Expense and payment summary for a group         |

---

## Sample API Commands

**List groups**
```bash
curl http://127.0.0.1:8000/api/groups/
```

**Create a group**
```bash
curl -X POST http://127.0.0.1:8000/api/groups/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Goa Trip", "description": "March expenses", "currency": "INR", "created_by": 1}'
```

**Add an expense — equal split**
```bash
curl -X POST http://127.0.0.1:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"group": 1, "description": "Hotel", "amount": 4500, "currency": "INR", "paid_by": 1}'
```

**Add an expense — custom split**
```bash
curl -X POST http://127.0.0.1:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "group": 1,
    "description": "Cab",
    "amount": 600,
    "currency": "INR",
    "paid_by": 2,
    "splits": [
      {"user": 1, "amount": 200},
      {"user": 2, "amount": 200},
      {"user": 3, "amount": 200}
    ]
  }'
```

**View balances**
```bash
curl http://127.0.0.1:8000/api/groups/1/balances/
```

**Get settle-up plan**
```bash
curl http://127.0.0.1:8000/api/expenses/group/1/settle-up/
```

**Record a payment**
```bash
curl -X POST http://127.0.0.1:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{"group": 1, "payee": 2, "amount": 1500, "note": "Paid back for hotel"}'
```

---

## Interview Task (for candidates)

**Scenario:** SplitMate is used by teams to track shared expenses during trips, events, and lunches. QA and real users have reported several issues.

**Your task:**

1. Explore the codebase — start with `expenses/views.py`, `groups/views.py`, `groups/serializers.py`, and `payments/views.py`
2. Reproduce each reported issue using the API or Django shell
3. Fix it with a minimal, focused change
4. Write a one-line comment above each fix: `# FIX: <what was wrong>`
5. Explain the root cause and how you confirmed the fix works

---

**Reported issues:**

- Splitting ₹101 between 2 people makes each person owe ₹50 — that totals ₹100. A rupee silently disappears. Same problem when splitting ₹100 three ways.
- A user reported they can see, edit, and delete a group they were never added to — just by changing the number in the URL.
- The balances page takes over 30 seconds to load when a group has more than 6 members. It used to be fast.
- One team added a $50 USD expense to their INR group. The balance looked correct on day one. Two weeks later — with no new expenses added — the balance changed on its own.
- A member clicked "Record Payment" twice because the page was slow. Now the app shows they paid double and the other person has a negative balance.
- The `/api/groups/1/` response contains fields like `_audit_hash` and `_created_from` that look like internal system data. Users are asking why they can see this.
- The `/api/groups/` list also shows every user's `last_login`, `date_joined`, and `is_staff` flag. This feels like more than clients should ever see.
- The group summary occasionally returns filter data from a previous request when running in production, but always works correctly in unit tests.

**Suggested time:** 45–60 minutes

---

## Project Structure

```
splitmate/
├── splitmate/           # Django project config
│   ├── settings.py
│   └── urls.py
├── groups/
│   ├── models.py        # Group model with members
│   ├── serializers.py   # API serialization
│   ├── views.py         # Group CRUD, member management, balances
│   └── urls.py
├── expenses/
│   ├── models.py        # Expense & ExpenseSplit models
│   ├── serializers.py   # Expense serialization
│   ├── views.py         # Expense creation, split logic, settle-up
│   └── urls.py
├── payments/
│   ├── models.py        # Payment (settlement) model
│   ├── views.py         # Payment creation, listing, group summary
│   └── urls.py
├── management/
│   └── commands/
│       └── seed_data.py # Sample data loader
├── manage.py
└── requirements.txt
```

---

## Useful Commands

| Command                                 | Description                           |
|-----------------------------------------|---------------------------------------|
| `python manage.py runserver`            | Start dev server                      |
| `python manage.py migrate`              | Apply database migrations             |
| `python manage.py seed_data`            | Load sample groups, users & expenses  |
| `python manage.py createsuperuser`      | Create admin user                     |
| `python manage.py shell`                | Open Django shell for debugging       |
| `python manage.py flush`                | Clear all data                        |

**Reset between interviews:**

```bash
python manage.py flush --no-input
python manage.py migrate
python manage.py seed_data
```

**Seed users** (password for all: `password123`):
`arjun`, `priya`, `rahul`, `sneha`, `vikram`
