# TaskHive: Resilient Microservices System

**Developed by Overclocked_Minds:** Shanon, Arana, Dola

. Built for the **BCF_26_Hackathon_Microservices_And_DevOps**.

---

## Key Features

- **Idempotency Shield:** Prevents "ghost" double-deductions using shared UUIDs and a transaction ledger.  
- **Chaos Simulation:** Integrated "Gremlin" (random latency) and "Ghost" (post-commit crashes) to test system stability.  
- **Real-time Monitoring:** Minimal dashboard to track service health, response times, and connection logs.  
- **Automated CI:** GitHub Actions workflow for continuous integration and smoke testing.  

---

## 💻 Tech Stack

- **Languages:** Python 3.13.7  
- **Backend:** Flask,   
- **Database:** PostgreSQL 18  
- **DevOps:** Docker, Docker Compose, GitHub Actions  

---

## 🛠️ Getting Started

### Clone the Repository
```bash
git clone https://github.com/RamisaRaidah/BCF_26_Hackathon_Final_Overclocked_Minds
cd BCF_26_Hackathon_Final_Overclocked_Minds
