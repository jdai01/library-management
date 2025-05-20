# Task 4 - Document Modeling: MongoDB

This task involves migrating the library backend database from PostgreSQL (relational) to MongoDB (NoSQL document-based) to leverage MongoDB’s schema flexibility and ease of evolving data structures.

1. **MongoDB Collections and Data Migration**
    - MongoDB collections were designed to mirror the previous PostgreSQL tables, but with embedded documents replacing many join tables, simplifying queries and improving data retrieval efficiency.
        - For example, book documents now embed arrays for authors, publishers, and genres directly within the same document.
    - Database initialisation was performed using an initialization script (`init_mongo.py`) that drops existing collections and loads initial data.

2. **Demonstration of Schema Flexibility**
    - A new attribute, `movie_release`, was added to the `books` collection documents to store related movie release dates.

3. **Updated Backend**
    - The Flask backend was updated to interact with MongoDB using PyMongo.

4. **Updated Development Environment**
    - `docker-compose.yaml` now includes:
        - `mongo` service running MongoDB
        - `mongo-express` for convenient database management via web UI


## Setup
1. Switch to the `mongo` branch
    ```bash
    git switch mongo
    ```

2. Build and Start the App Containers
    ```bash
    docker compose up --build
    ```

3. Access Interfaces
    - MongoDB Interface:  
        View and manage your database in the browser: [Click here](http://127.0.0.1:8081)  
        with `username=admin` and `password=pass`.

    - Library App Interface:  
        Access the main Flask application: [Click here](http://127.0.0.1:5001)

4. Stop and Remove Containers
    ```bash
    docker compose down
    ```