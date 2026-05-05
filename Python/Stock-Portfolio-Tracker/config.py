# config.py
# ─────────────────────────────────────────────
# Central configuration loader.
# All secrets are read from the .env file.
# Never hardcode credentials in source code.
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# ── Email credentials ─────────────────────────
EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ── Database ──────────────────────────────────
DB_NAME = os.getenv("DB_NAME", "portfolio_history.db")

# ── Portfolio definition ──────────────────────
PORTFOLIO = {
    "RDW": {
        "shares"  : int(os.getenv("RDW_SHARES",   608)),
        "avg_cost": float(os.getenv("RDW_AVG_COST", 8.99)),
        "target"  : float(os.getenv("RDW_TARGET",  13.71))
    },
    "UEC": {
        "shares"  : int(os.getenv("UEC_SHARES",   70)),
        "avg_cost": float(os.getenv("UEC_AVG_COST", 14.67)),
        "target"  : float(os.getenv("UEC_TARGET",  18.95))
    }
}
