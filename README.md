## 🧩 Overview
Finance Tracker is a lightweight financial management application that helps users keep track of their spending and earnings. It supports adding and editing transactions, organizing them by category and date,
and displaying helpful charts to understand financial habits and gain better insights. The app is built with Streamlit and uses MongoDB Atlas to store data securely and reliably.

## ⭐ Features
- Manage categories (add, edit, delete)
- Add, edit, and delete transactions  
- Organize data by category and date
- Dashboard showing income and expenses  
- Interactive charts for financial insights
- MongoDB Atlas storage

## 🧰 Tech Stack

- **Frontend:** Streamlit 
- **Database:** MongoDB Atlas  
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Data Handling:** Pandas  
- **Environment Config:** python-dotenv (local), Streamlit Secrets (deployment)
  
## 📦 Installation
### Step 1. Clone the project
```bash
git clone https://github.com/ZyroFrost/finance_tracker.git
cd finance_tracker
```

### Step 2. Create a virtual environment
```bash
python -m venv .venv
```

Activate it:
- Windows
```bash
.venv\Scripts\activate
```

- macOS / Linux
```bash
source .venv/bin/activate
```

### Step 3. Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4. Set Up MongoDB Atlas Connection
- You need a database connection string. Follow the MongoDB Atlas setup steps::
  - Go to https://www.mongodb.com/cloud/atlas
  - Create a free account
  - Create a free cluster
  - Create database credentials (username + password)
  - Get your connection string
  - You can check your created database users in:
  **MongoDB Atlas → Security → Database Access**

### Step 5. Create a .env file in the project
- After you get your connection string, create a `.env` file and add:

```bash
MONGO_URI=mongodb+srv://username:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=finance_tracker
```
- **Important**: Make sure .env is in .gitignore. It contains secrets and should not be public.

### Step 6. Set Up Google Authentication (optional)
- This step is required only if you use Google Login (OAuth)
- If you don't have Google OAuth, follow this guide:
https://medium.com/@tony.infisical/guide-to-using-oauth-2-0-to-access-google-apis-dead94d6866d

### Step 7. Create .streamlit/secrets.toml
- If you are using Google OAuth, create the file in project root:
```bash
.streamlit/secrets.toml
```
- Add the following:
```bash
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret-key"
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```
- **Important**: Make sure .streamlit/secrets.toml is in .gitignore. It contains secrets and should not be public.

## ▶️ Running the App
- After completing the setup, start the app with:
```bash
streamlit run src/app.py
```

## 🚀 Deployment (optional)
### Step 1. Push your project to GitHub
- If you haven't pushed your project yet:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin 'your repository link'
git push -u origin main
```

- If the project already exists, just update it with:
```bash
git add .
git commit -m "Update project"
git push
```

### Step 2. Go to Streamlit Cloud
- Link: https://share.streamlit.io
- Create a new app:

  - Select your GitHub repository
  - Select branch: main
  - Set the main file to src/app.py
 
### Step 3. Add Secrets (Environment Variables)
- Go to Settings → Secrets and paste:

```bash
MONGO_URI="your-mongodb-uri"
DATABASE_NAME="finance_tracker"

# If using Google OAuth:
[auth]
redirect_uri = "https://your-app-url.streamlit.app/oauth2callback"
cookie_secret = "your-random-secret-key"
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

### Step 4. Deploy the app
- Click Deploy and Streamlit Cloud will host the app automatically
```bash
https://personal-cashflow.streamlit.app
```

### Step 5. Update the deployed app (very important)
- Every time you change the code:
```bash
git add .
git commit -m "Update app"
git push
```

## 📁 Project structure in local (How It Should Look)
```bash
.
└── finance_tracker/
    ├── .streamlit/
    │   ├── config.toml
    │   └── secrets.toml
    ├── .env
    ├── .gitignore
    ├── .vscode
    ├── src/
    │   ├── app.py
    │   ├── utils.py
    │   ├── analytics/
    │   │   ├── analyzer.py
    │   │   └── visualizer.py
    │   ├── assets/
    │   │   ├── google_logo.png
    │   │   ├── logo.png
    │   │   ├── icon.png
    │   │   └── styles.py
    │   ├── core/
    │   │   ├── database_manager.py
    │   │   └── config.py
    │   ├── models/
    │   │   ├── user_model.py
    │   │   ├── category_model.py
    │   │   ├── exchange_rate_model.py
    │   │   ├── transaction_model.py
    │   │   └── budget_model.py
    │   └── views/
    │       ├── dashboard_view.py
    │       ├── categories_view.py
    │       ├── settings_view.py
    │       ├── transactions_view.py
    │       └── budgets_view.py
    ├── requirements.txt
    └── README.md
```
## 🖼️ App Screenshots
<img width="1791" height="890" alt="image" src="https://github.com/user-attachments/assets/b407b972-96a0-4ec4-afae-79216aef09b9" />
<img width="1832" height="910" alt="image" src="https://github.com/user-attachments/assets/c474ef2d-4317-4971-a8cb-b3a38989a785" />
<img width="1797" height="644" alt="image" src="https://github.com/user-attachments/assets/81f1076e-1638-47ca-b2e7-7abd99d54707" />
<img width="1820" height="875" alt="image" src="https://github.com/user-attachments/assets/0c2e4a73-bb19-4904-938a-08ba3f8d68c8" />
<img width="1802" height="785" alt="image" src="https://github.com/user-attachments/assets/55573b17-6818-4705-b8fe-cc012d361a1c" />
<img width="1797" height="644" alt="image" src="https://github.com/user-attachments/assets/a9c7f24a-67ee-48ef-af59-1651aabafa5d" /># 📊 Finance Tracker – Streamlit + MongoDB

# Submission Checklist
## 🎯 Selected topics and total points
- Budget Management System (Full CRUD): 6 points
- Orphaned Transactions – Category Deletion: 3 points
- User Deletion – Data Leak Prevention: 3 points
- Category Update – Transaction Sync: 3 points
- Budget Integrity – Category Deletion Impact: 2 points
- Transaction Category Validation: 3 points

Total: 20 points

## 🛡️ Data Integrity Strategies Chosen

### 1. Budget Management System (6 points)
- Full CRUD operations for budgets (create, read, update, delete)
- Compound unique index: `(user_id, category_id, budget_type, month, year)`
- Progress calculation using MongoDB aggregation (`$match` + `$group`)
- UI with color-coded progress bars
- Implementation: `budget_model.py`, `budgets_view.py`, `transaction_model.py` (frontend + backend)

### 2. Orphaned Transactions - Category Deletion (3 points)
- Count affected transactions and budgets before deletion
- User choice: Reassign to another category OR Cascade delete
- MongoDB operations: `update_many()` for reassign, `delete_many()` for cascade
- Warning dialogs with exact counts
- Implementation: `category_model.py`, `categories_view.py` (frontend + backend)

### 3. User Deletion - Data Leak Prevention (3 points)
- MongoDB transaction ensures atomic deletion of all user data
- Deletes: transactions, budgets, custom categories, user document
- Confirmation dialog with data summary
- Rollback protection (all-or-nothing)
- Implementation: `user_model.py`, `settings_view.py` (frontend + backend)

### 4. Category Update - Transaction Sync Problem (3 points)
- ObjectId-based relationships (transactions reference category by ID, not name)
- Automatic sync when category renamed (no manual updates needed)
- Duplicate name validation within same type
- Edit form with transaction count display
- Implementation: `category_model.py`, `transactions_view.py` (frontend + backend)

### 5. Budget Integrity - Category Deletion Impact (2 points)
- Category deletion also handles related budgets
- Budgets either reassigned or deleted based on user strategy
- Budget count shown in deletion warning
- Integrated with category deletion flow
- Implementation: `category_model.py`, `budget_model.py` (frontend + backend)

### 6. Transaction Category Validation (3 points)
- Validate category exists before creating/updating transaction
- Frontend: Dropdown restricted to valid categories
- Backend: Database checks with clear error messages
- User-scoped validation (category must belong to user)
- Implementation: `transaction_model.py`, `transactions_view.py` (frontend + backend)

### 7. Bonus - Multi-Currency Support with Exchange Rate Management
- 6 supported currencies: USD, VND, JPY, EUR, CNY, AUD
- Automatic currency conversion for all transactions and budgets
- Real-time exchange rates from ExchangeRate-API
- Smart caching: Rates cached for 24 hours to minimize API calls
- User preference: Each user can set default display currency
