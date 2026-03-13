from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import os

load_dotenv()

from graph.pipeline import run_price_pipeline
from utils.auth import request_otp, verify_otp, save_tracked_product, get_user_tracked_products

app = FastAPI(
    title="AI Price Intelligence API",
    description="5-agent AI system that tracks prices and predicts best time to buy",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class SearchRequest(BaseModel):
    product_name: str
    user_email: str

class StatusUpdate(BaseModel):
    product_id: int
    status: str

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str

class TrackRequest(BaseModel):
    user_id: str
    product_name: str
    price: str
    url: str
    platform: str = "Amazon"

@app.get("/")
def home():
    return {"status": "running", "message": "AI Price Intelligence API is live! 🚀", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_product(request: SearchRequest):
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
            "alternatives_found": result["alternatives_found"],
            "best_product": result.get("best_product", {})
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/tracked")
def get_tracked_products():
    tracked_file = "data/tracked_products.json"
    if os.path.exists(tracked_file):
        with open(tracked_file, "r") as f:
            content = f.read().strip()
            tracked = json.loads(content) if content else []
    else:
        tracked = []
    return {"success": True, "total": len(tracked), "products": tracked}

@app.put("/tracked/status")
def update_status(update: StatusUpdate):
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
    tracked_file = "data/tracked_products.json"
    with open(tracked_file, "r") as f:
        tracked = json.load(f)
    tracked = [p for p in tracked if p["id"] != product_id]
    with open(tracked_file, "w") as f:
        json.dump(tracked, f, indent=2)
    return {"success": True, "message": "Product removed!"}

@app.post("/auth/request-otp")
async def request_otp_endpoint(req: OTPRequest):
    return request_otp(req.email)

@app.post("/auth/verify-otp")
async def verify_otp_endpoint(req: OTPVerify):
    return verify_otp(req.email, req.otp)

@app.post("/track")
async def track_product(req: TrackRequest):
    success = save_tracked_product(
        req.user_id, req.product_name,
        req.price, req.url, req.platform
    )
    return {"success": success}

@app.get("/my-products/{user_id}")
async def get_my_products(user_id: str):
    products = get_user_tracked_products(user_id)
    return {"success": True, "products": products}