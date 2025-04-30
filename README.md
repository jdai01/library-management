# CAI_DBBDPr
Database Systems and Big Data Technologies Practical

## Tasks
1. [Conceptual Modeling: Design an ER Diagram](content/Task1.md)
2. [Relational DB (PostgreSQL)](content/Task2.md)
3. [User Behavior Analytics (MongoDB)](content/Task3.md)
4. [Recommendation System (Neo4j)](content/Task4.md)


## Installation Guide
1. Clone Repository
    ```bash
    git clone https://github.com/jdai01/library_management
    cd library_management
    ```

2. Build the App Images
    ```bash
    docker compose build
    ```

3. Start the App Containers
    ```bash
    docker compose up
    ```

4. Access Interfaces
    - PostgreSQL Adminer Interface:  
        View and manage your database in the browser: [Click here](http://127.0.0.1:8080/?pgsql=library)

    - Library App Interface:  
        Access the main Flask application: [Click here](http://127.0.0.1:5001)

5. Stop and Remove Containers
    ```bash
    docker compose down
    ```
