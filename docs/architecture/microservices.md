#  Microservices Architecture Documentation

##  Overview
This document outlines the microservices architecture for our project. We have decoupled our application into lightweight, independent services to ensure scalability, fault tolerance, and easier deployment.

**Tech Stack:**
* **Backend:** Python (Flask) 
* **Database:** PostgreSQL 
* **Containerization:** Docker & Docker Compose 
* **Deployment:** !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

---

## The Services

### 1. `[orders_service]` 
* **Purpose:** Handles user requests, validates orders, and orchestrates stock deduction.
* **Port:** Runs on `8000`.
* **Database:** Connects to the `users_db` container.
* **Key Tech:** Flask,Flask-RESTful,psycopg2-binary,pytest,flask-jwt-extended

### 2. `[inventory_service]` 
* **Purpose:** Manages product stock and ensures data consistency.
* **Port:** Runs on `8001`.
* **Database:** Connects to the `inventory_db` container.
* **Key Tech:** Flask, Flask-RESTful, psycopg2-binary, pytest, flask-jwt-extended

---

## How to Run Locally (For Devs & Testers)

**Prerequisites:**
* Docker & Docker Compose installed.

**Steps:**
1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/RamisaRaidah/BCF_26_Hackathon_Final_Overclocked_Minds
    cd BCF_26_Hackathon_Final_Overclocked_Minds
    ```

2.  **Fire it up:**
    ```bash
    docker-compose up --build
    ```

3.  **Access the App:**
    * API is live at:  //pore edit korbaaaaa!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

---

##  Deployment (CI/CD)
* **Live URL:** !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!