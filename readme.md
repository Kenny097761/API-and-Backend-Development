# IoTBay Marketplace Workshop Project

This repository contains the IoTBay Marketplace web application with:

- A Flask backend in `backend/`
- Static frontend pages in `frontend/`
- A SQLite database setup under `backend/models/`


## Project Structure

```text
backend/
  app.py                        Flask application entrypoint
  models/
    db_connect.py               SQLite connection helper
    db_init.py                  Database schema initialization
    db_crud.py                  Placeholder CRUD module
    access_logs_service.py
    payment_method_crud.py
    payment_method.py
    shipment.py
  routes/
    access_logs_routes.py
    auth_routes.py
    device_routes.py
    orders.py
    payment_methods.py
    payments.py
    shipments.py

frontend/
    index.html
    login.html
    register.html
    update_user.html
    welcome.html
    access-logs.html
    catalogue.html
    make-payment.html
    my-shipments.html
    orders.html
    payment-history.html
    paymentMethods.html
    profile.html
    shipment-detail.html
    staff-payments.html
  css/
  js/
```

## Prerequisites

- Python 3.10+ recommended
- `pip` / `pip3`

## Local Setup

From the repository root, create and activate a virtual environment, then install Flask.

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install flask
```

## Backend Setup And Run

From the repository root, run the following commands in order:

### macOS

```bash
pip install flask
pip install flask-cors
python3 -m backend.models.db_init
python3 -m backend.app
```

### Windows

```bat
pip install flask
pip install flask-cors
python -m backend.models.db_init
python -m backend.app
```

What each command does:

- `pip install flask` installs Flask into the active virtual environment
- `pip install flask-cors` enables Cross-Origin Resource Sharing (CORS) between the frontend and backend applications
- `python -m backend.models.db_init` creates the local SQLite database
- `python -m backend.app` starts the Flask development server

The backend runs at:


http://127.0.0.1:8080



## Run The Frontend


### macOS

```bash
cd frontend
python3 -m http.server 5500
```

### Windows

```bat
cd frontend
python -m http.server 5500
```

Then open pages directly in the browser:

- `http://127.0.0.1:5500/index.html`
- `http://127.0.0.1:5500/register.html`
- `http://127.0.0.1:5500/login.html`
- `http://127.0.0.1:5500/welcome.html`
- `http://127.0.0.1:5500/update_user.html`
  
- `http://127.0.0.1:5500/access-logs.html`
- `http://127.0.0.1:5500/catalogue.html`
- `http://127.0.0.1:5500/make-payment.html`
- `http://127.0.0.1:5500/my-shipments.html`
- `http://127.0.0.1:5500/orders.html`
- `http://127.0.0.1:5500/payment-history.html`
- `http://127.0.0.1:5500/paymentMethods.html`
- `http://127.0.0.1:5500/profile.html`
- `http://127.0.0.1:5500/shipment-detail.html`
- `http://127.0.0.1:5500/staff-payments.html`

## Database

The project uses SQLite.

- Database file: `backend/app.db`
- Connection helper: `backend/models/db_connect.py`
- Schema initialization: `backend/models/db_init.py`

## Database Test Script

to showcase database connection run: 
```bash
python -m backend.test.show_db_connection (win)
python3 -m backend.test.show_db_connection (mac)
```

## Shipments Readme 
feature for Assignment 2. Covers US-701 (view), US-702 (create), US-703 (update + soft cancel), US-704.

### Setup

Install deps:
```bash
python3 -m pip install flask flask-cors pytest playwright
```

For the e2e browser test only:
```bash
playwright install chromium
```

### Running it

Two terminals from the repo root.

Reset the db (run this once, or whenever you want fresh seed data):

```bash
rm backend/app.db
python3 -m backend.models.db_init
```

Start Backend:

```bash
python3 -m backend.app
```

Start Frontend (new terminal):

```bash
cd frontend
python3 -m http.server 5500
```

Then open http://127.0.0.1:5500/welcome.html.

### Demo accounts

Password for all of them is `password123`.

- Alice Nguyen (customer, user_id 1) - alice@iotbay.com
- Bob Smith (customer, user_id 2) - bob@iotbay.com
- Diana Lee (staff, user_id 3) - staff1@iotbay.com
- Evan Park (staff, user_id 4) - staff2@iotbay.com

### Walkthrough

1. Become staff Diana, open `create-shipment.html`, pick a paid order, click Create. The order disappears from the dropdown.
2. Become Alice, open `my-shipments.html` - she sees her shipments. No edit buttons (she's a customer).
3. Click into one to view details. Customers just see info, no controls.
4. Switch back to Diana and reopen the detail page. The Update form is there with `shipped` as the next step. Click through pending -> shipped -> delivered. For pending shipments theres also a red Cancel button which sets status to `cancelled` (soft delete, the row stays for audit).

### Tests

```bash
pytest backend/tests/ -k "not e2e"
```

That runs the unit + API tests (19 total). The e2e test needs both servers running and shipment 1 in pending state:

```bash
rm backend/app.db && python3 -m backend.models.db_init
pytest backend/tests/test_shipments_e2e.py
```

If servers aren't up the e2e test skips rather than failing.

</details>
