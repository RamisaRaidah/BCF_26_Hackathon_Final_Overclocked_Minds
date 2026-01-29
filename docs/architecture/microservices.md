#  Microservices Architecture Documentation

##  Overview
This document outlines the microservices architecture for our project. We have decoupled our application into lightweight, independent services to ensure scalability, fault tolerance, and easier deployment.

**Tech Stack:**
* **Backend:** Python (Flask) 
* **Database:** PostgreSQL 
* **Containerization:** Docker & Docker Compose 
* **Deployment:** Inventory:  https://bcf-26-hackathon-final-overclocked-minds-a2yl.onrender.com/
                  Order:      https://bcf-26-hackathon-final-overclocked-minds-cu7q.onrender.com/
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

##  Deployment (CI/CD)
* **Live URL:** Inventory:  https://bcf-26-hackathon-final-overclocked-minds-a2yl.onrender.com/
                Order:      https://bcf-26-hackathon-final-overclocked-minds-cu7q.onrender.com/