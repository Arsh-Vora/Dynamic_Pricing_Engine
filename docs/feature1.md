### **Feature 1: Core Application Setup & Product Registration API**

**Objective:** Create a fully functional, containerized, multi-service application on your local machine. This feature will deliver a React form that successfully submits device data to a FastAPI backend, which then saves it to a PostgreSQL database.

**Git Branch Name:** `feature/1-core-setup-registration`

---

#### **Detailed Plan for Feature 1:**

**Step 1: Project Scaffolding & Docker Setup**

1.  **Create Project Structure:** On your local machine, create a root folder for the project (e.g., `recommerce_app`). Inside it, create `backend` and `frontend` folders.
    ```
    recommerce_app/
    ├── backend/
    ├── frontend/
    └── docker-compose.yml  <-- We will create this
    ```

2.  **Initialize Git:** In the `recommerce_app` root folder, run `git init`.

3.  **Create `docker-compose.yml`:** In the root folder, create a `docker-compose.yml` file. This file is the "master remote control" for our application.

    ```yaml
    # In docker-compose.yml
    version: '3.8'
    services:
      db:
        image: postgres:15
        container_name: recommerce_db
        environment:
          - POSTGRES_USER=admin
          - POSTGRES_PASSWORD=secret
          - POSTGRES_DB=recommerce
        ports:
          - "5432:5432"
        volumes:
          - postgres_data:/var/lib/postgresql/data/

      backend:
        container_name: recommerce_backend
        build: ./backend  # Tells Docker to build the image from the backend folder
        ports:
          - "8000:8000"
        volumes:
          - ./backend:/app # Mounts your code for live reloading
        depends_on:
          - db

    volumes:
      postgres_data:
    ```
    *This sets up a PostgreSQL database and our future backend service.*

**Step 2: Backend Development (FastAPI)**

1.  **Create Backend Files:** Inside the `backend` folder, create a `Dockerfile`, a `requirements.txt`, and an `app` sub-folder for your code.
    *   **`backend/Dockerfile`**:
        ```dockerfile
        FROM python:3.11-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY . .
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        ```
    *   **`backend/requirements.txt`**:
        ```
        fastapi
        uvicorn[standard]
        sqlalchemy
        psycopg2-binary
        pydantic[email]
        ```

2.  **Write the Python Code:**
    *   **Database Model (`backend/app/models.py`):** Define your `Product` table using SQLAlchemy. (Fields: `id`, `device_model`, `condition`, `age_in_months`, `status`, `initial_offer_price`, `created_at`).
    *   **Data Schemas (`backend/app/schemas.py`):** Create Pydantic schemas for data validation (`ProductCreate`, `ProductResponse`).
    *   **Database Connection (`backend/app/database.py`):** Set up SQLAlchemy to connect to the PostgreSQL Docker container.
    *   **API Endpoint (`backend/app/api/products.py`):** Create a new FastAPI router. Define the `POST /register` endpoint. Its logic will:
        a.  Accept a `ProductCreate` JSON object.
        b.  Create a new `Product` model instance with `status="Registered"`.
        c.  Save it to the database.
        d.  Return the new product object.
    *   **Main App (`backend/app/main.py`):** Create the main FastAPI app instance and include your product router.

**Step 3: Frontend Development (React + Vite)**

1.  **Scaffold the React App:**
    *   Open your terminal, navigate into the `frontend` folder: `cd frontend`.
    *   Run `npm create vite@latest . -- --template react-ts`. (The `.` installs it in the current folder). Follow the prompts.
2.  **Build the Submission Form:**
    *   Create a new component `src/components/ProductSubmissionForm.tsx`.
    *   Build a simple form with inputs for model, condition (dropdown), and age.
    *   Add a submit button.
3.  **Implement API Communication:**
    *   In your form component, write an `async handleSubmit` function.
    *   This function will use `fetch` to make a `POST` request to `/api/v1/products/register`.
4.  **Configure Vite Proxy (to avoid CORS errors):**
    *   This is a critical step for local development.
    *   Open the `vite.config.ts` file in your `frontend` folder.
    *   Add a `server.proxy` configuration to tell Vite that any request to `/api` should be forwarded to your backend running on port 8000.
        ```typescript
        // In vite.config.ts
        import { defineConfig } from 'vite'
        import react from '@vitejs/plugin-react'

        export default defineConfig({
          plugins: [react()],
          server: {
            proxy: {
              '/api': {
                target: 'http://localhost:8000', // Your FastAPI backend
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''), // Optional: remove /api prefix
              },
            },
          },
        })
        ```

**Step 4: Launch and Test**

1.  **Launch Docker:** From the **root** `recommerce_app` folder in your terminal, run:
    ```bash
    docker-compose up --build
    ```
    This one command will build your backend image, start the PostgreSQL database, and run your backend service.

2.  **Launch Frontend:** In a **second terminal**, navigate into the `frontend` folder (`cd frontend`) and run:
    ```bash
    npm install
    npm run dev
    ```
3.  **Test:** Open your browser to the URL Vite provides (e.g., `http://localhost:5173`). You should see your React form. Fill it out, submit it, and check your backend terminal logs and database to confirm the data was saved.
