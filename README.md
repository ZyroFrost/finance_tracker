# 📊 Finance Tracker – Streamlit + MongoDB
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
https://your-app-name.streamlit.app
```

### Step 5. Update the deployed app (very important)
- Every time you change the code:
```bash
git add .
git commit -m "Update app"
git push
```

## Project structure in local (How It Should Look)
```bash
.
└── finance_tracker/
    ├── .streamlit/
    │   └── secrets.toml
    ├── .env
    ├── .gitignore
    ├── requirements.txt
    └── src/
        ├── app.py
        ├── utils.py
        ├── analytics/
        │   ├── __init__.py
        │   ├── analyzer.py
        │   └── visualizer.py
        ├── assets/
        │   ├── google_logo.png
        │   ├── logo.png
        │   ├── icon.png
        │   └── styles.py
        ├── core/
        │   ├── __init__.py
        │   ├── database_manager.py
        │   └── config.py
        ├── models/
        │   ├── __init__.py
        │   ├── category_model.py
        │   ├── exchange_rate_model.py
        │   ├── transaction_model.py
        │   └── user_model.py
        └── views/
            ├── __init__.py
            ├── dashboard_view.py
            ├── categories_view.py
            ├── settings_view.py
            └── transactions_view.py
```
