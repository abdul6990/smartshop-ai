from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import os

load_dotenv()

from graph.pipeline import run_price_pipeline

# ── CREATE APP ────────────────────────────────────
app = FastAPI(
    title="AI Price Intelligence API",
    description="5-agent AI system that tracks prices and predicts best time to buy",
    version="1.0.0"
)

# ── CORS (allows React Native to talk to this API) ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── REQUEST MODELS ────────────────────────────────
class SearchRequest(BaseModel):
    product_name: str
    user_email: str

class StatusUpdate(BaseModel):
    product_id: int
    status: str

# ── ROUTES (API endpoints) ────────────────────────

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "AI Price Intelligence API is live! 🚀",
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze_product(request: SearchRequest):
    """
    Main endpoint - runs all 5 agents
    Takes product name + email
    Returns AI prediction + research
    """
    try:
        result = run_price_pipeline(
            product_name=request.product_name,
            user_email=request.user_email
        )
        return {
            "success": True,
            "product_name": request.product_name,
            "ai_prediction": result["ai_prediction"],
            "alert_status": result["alert_status"],
            "products_found": result["products_found"],
            "alternatives_found": result["alternatives_found"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/tracked")
def get_tracked_products():
    """
    Returns all tracked products
    """
    tracked_file = "data/tracked_products.json"
    if os.path.exists(tracked_file):
        with open(tracked_file, "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    else:
        tracked = []
    return {
        "success": True,
        "total": len(tracked),
        "products": tracked
    }

@app.put("/tracked/status")
def update_status(update: StatusUpdate):
    """
    Updates status of a tracked product
    """
    tracked_file = "data/tracked_products.json"
    with open(tracked_file, "r") as f:
        tracked = json.load(f)
    
    for product in tracked:
        if product["id"] == update.product_id:
            product["status"] = update.status
            break
    
    with open(tracked_file, "w") as f:
        json.dump(tracked, f, indent=2)
    
    return {"success": True, "message": "Status updated!"}

@app.delete("/tracked/{product_id}")
def delete_product(product_id: int):
    """
    Removes a product from tracking
    """
    tracked_file = "data/tracked_products.json"
    with open(tracked_file, "r") as f:
        tracked = json.load(f)
    
    tracked = [p for p in tracked if p["id"] != product_id]
    
    with open(tracked_file, "w") as f:
        json.dump(tracked, f, indent=2)
    
    return {"success": True, "message": "Product removed!"}