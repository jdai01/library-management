# Task 3 - Graph Modeling: Neo4j

This task migrates the relational PostgreSQL library management system to a graph-based model using Neo4j, enabling more intuitive and flexible data relationships.

1. **Graph Data Modeling**

- Nodes (Entities)  
    The following main entities from the relational schema are modeled as nodes:
    - `User` – represents a library user.
    - `Book` – represents a book in the collection.
    - `Author` – represents a book’s author.
    - `Genre` – represents the genre/category of a book.
    - `Publisher` – represents the genre/category of a book.

- Relationships (Edges)  
    Relationships describe interactions or associations between entities:
    - `(:Book)-[:WRITTEN_BY]->(:Author)` – links a book to its author.
    - `(:Book)-[:HAS_GENRE]->(:Genre)` – links a book to its genre.
    - `(:Book)-[:PUBLISHED_BY]->(:Publisher)` – links a book to its publisher.
    - `(:User)-[:BORROWED]->(:Book)` – records when a user borrows a book
    - `(:User)-[:RETURNED]->(:Book)` – records when a user returns a book

2. **Updated Backend**  
    - The Flask backend was updated to use the official Neo4j Python driver.

3. **Updated Development Environment**
    - `docker-compose.yaml` now includes:
        - `neo4j` service running Neo4j



## Setup
1. Switch to the `neo4j` branch
    ```bash
    git switch neo4j
    ```

2. Build and Start the App Containers
    ```bash
    docker compose up --build
    ```

3. Access Interfaces
    - Neo4j Interface:  
        View and manage your database in the browser: [Click here](http://127.0.0.1:7474)

    - Library App Interface:  
        Access the main Flask application: [Click here](http://127.0.0.1:5001)

4. Stop and Remove Containers
    ```bash
    docker compose down
    ```