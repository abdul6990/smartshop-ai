from graph.pipeline import run_price_pipeline

result = run_price_pipeline(
    product_name="Samsung Galaxy S24",
    user_email="neelsyedabdulrehaman@gmail.com"
)

print("\n" + "="*50)
print("🤖 AI PREDICTION:")
print("="*50)
print(result["ai_prediction"])
print("\n🔔 Alert Status:", result["alert_status"])