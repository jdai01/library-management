# Task 2 - Relational Modeling: Postgres DB

## 1. Dockerized Application Stack
- A `Dockerfile` and `docker-compose.yaml` are provided to streamline setup.
- `docker-compose.yaml` spins up:
    - A PostgreSQL container (`db`) for data persistence
    - An Admire (Admirer) container (`adminer`) for DB inspection via web UI
    - A Flask application container (`app`) for serving the frontend/backend

## 2. Relational Database Design 
- The original ER diagram has been translated into a relational schema (`schema.sql`)
- Initial demo data is inserted using `data.sql` <!-- to showcase application functionality -->

## 3. Update Flask Backend
- Replaced XML data handling with PostgreSQL queries
- Established a connection to the PostgreSQL database using `psycopg2`
- Functional endpoints:
    - View available books and current borrowings (`index.html`, `viewer.html`)
    - Borrow and return books with proper SQL-based state updates
    - Clear all data functionality also handled via SQL


## Setup
1. Switch to the `postgres` branch
    ```bash
    git switch postgres
    ```

2. Build and Start the App Containers
    ```bash
    docker compose up --build
    ```

3. Access Interfaces
    - PostgreSQL Adminer Interface:  
        View and manage database in the browser: [Click here](http://127.0.0.1:8080/?pgsql=library)

    - Library App Interface:  
        Access the main Flask application: [Click here](http://127.0.0.1:5001)

4. Stop and Remove Containers
    ```bash
    docker compose down
    ```