
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).resolve().parent / "cybertwin.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                scenario_name TEXT NOT NULL,
                target TEXT NOT NULL,
                severity TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                attack_path TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="CyberTwin AI",
    description="Cybersecurity Risk Simulation API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class SimulationRequest(BaseModel):
    scenario: str = Field(min_length=1, max_length=100)
    target: str = Field(
        default="Demo Network",
        min_length=1,
        max_length=100
    )
    severity: str = "medium"


SCENARIOS = {
    "phishing": {
        "name": "Phishing Risk",
        "base": 65,
        "path": ["Email Gateway", "User Account", "Demo Application"],
        "recommendations": [
            "Enable multi-factor authentication.",
            "Train users to identify phishing emails.",
            "Configure email filtering."
        ]
    },
    "weak_password": {
        "name": "Weak Password Risk",
        "base": 75,
        "path": ["Login Portal", "User Account", "Demo Application"],
        "recommendations": [
            "Use long, unique passwords.",
            "Enable multi-factor authentication.",
            "Apply login rate limits."
        ]
    },
    "misconfiguration": {
        "name": "Misconfiguration Risk",
        "base": 60,
        "path": ["Demo Server", "Network Service", "Demo Database"],
        "recommendations": [
            "Review system configurations.",
            "Disable unnecessary services.",
            "Apply least-privilege access."
        ]
    },
    "malware": {
        "name": "Malware Risk",
        "base": 80,
        "path": ["User Device", "Demo Endpoint", "Demo Network"],
        "recommendations": [
            "Keep software updated.",
            "Use endpoint protection.",
            "Maintain secure backups."
        ]
    },
    "ddos": {
        "name": "DDoS Risk",
        "base": 85,
        "path": ["Public Endpoint", "Network Gateway", "Demo Service"],
        "recommendations": [
            "Configure rate limiting.",
            "Use DDoS protection services.",
            "Monitor network traffic."
        ]
    }
}

MULTIPLIERS = {"low": 0.6, "medium": 1.0, "high": 1.3}


def calculate_risk(base, severity):
    return min(100, round(base * MULTIPLIERS[severity]))


def get_risk_level(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def save_simulation(result):
    with get_connection() as db:
        cursor = db.execute("""
            INSERT INTO simulations (
                scenario_id, scenario_name, target, severity,
                risk_score, risk_level, attack_path,
                recommendations, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["scenario_id"],
            result["scenario_name"],
            result["target"],
            result["severity"],
            result["risk_score"],
            result["risk_level"],
            " -> ".join(result["attack_path"]),
            " | ".join(result["recommendations"]),
            result["created_at"]
        ))
        return cursor.lastrowid


def format_simulation(row):
    item = dict(row)
    item["attack_path"] = item["attack_path"].split(" -> ")
    item["recommendations"] = item["recommendations"].split(" | ")
    item["simulation_only"] = True
    return item


@app.get("/")
def home():
    return {
        "project": "CyberTwin AI",
        "status": "running",
        "database": "SQLite",
        "documentation": "/docs"
    }


@app.get("/api/health")
def health():
    with get_connection() as db:
        db.execute("SELECT 1")
    return {
        "api_status": "healthy",
        "database_status": "connected",
        "database": "SQLite"
    }


@app.get("/api/dashboard")
def dashboard():
    with get_connection() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM simulations"
        ).fetchone()[0]
        high = db.execute(
            "SELECT COUNT(*) FROM simulations WHERE risk_level = ?",
            ("High",)
        ).fetchone()[0]
        medium = db.execute(
            "SELECT COUNT(*) FROM simulations WHERE risk_level = ?",
            ("Medium",)
        ).fetchone()[0]
        low = db.execute(
            "SELECT COUNT(*) FROM simulations WHERE risk_level = ?",
            ("Low",)
        ).fetchone()[0]

    return {
        "project": "CyberTwin AI",
        "total_simulations": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "available_scenarios": len(SCENARIOS)
    }


@app.get("/api/scenarios")
def get_scenarios():
    return [
        {
            "id": key,
            "name": value["name"],
            "description": f"Simulated {value['name'].lower()} scenario"
        }
        for key, value in SCENARIOS.items()
    ]


@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    scenario_id = request.scenario.strip().lower()
    severity = request.severity.strip().lower()
    target = request.target.strip()

    if scenario_id not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail={"message": "Unknown scenario",
                    "available_scenarios": list(SCENARIOS.keys())}
        )

    if severity not in MULTIPLIERS:
        raise HTTPException(
            status_code=400,
            detail="Severity must be low, medium, or high."
        )

    if not target:
        raise HTTPException(status_code=400, detail="Target cannot be empty.")

    scenario = SCENARIOS[scenario_id]
    score = calculate_risk(scenario["base"], severity)

    result = {
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "target": target,
        "severity": severity,
        "risk_score": score,
        "risk_level": get_risk_level(score),
        "attack_path": scenario["path"],
        "recommendations": scenario["recommendations"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "simulation_only": True
    }

    result["id"] = save_simulation(result)
    return result


@app.get("/api/simulations")
def get_history(limit: int = Query(default=20, ge=1, le=100)):
    with get_connection() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM simulations"
        ).fetchone()[0]
        rows = db.execute(
            "SELECT * FROM simulations ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return {"items": [format_simulation(row) for row in rows], "total": total}


@app.get("/api/simulations/latest")
def get_latest():
    with get_connection() as db:
        row = db.execute(
            "SELECT * FROM simulations ORDER BY id DESC LIMIT 1"
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="No simulations found.")

    return format_simulation(row)



