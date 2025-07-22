from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()


# Load allowed origins from env var or fallback to default list
# origins = os.getenv("FRONTEND_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],  # only GET requests allowed
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "User-Agent", "X-Requested-With"],
)

# Fetch conversion rate from source to target
def fetch_conversion_factor(source: str, target: str) -> float:
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_R4Y6eMxoYwSsGlM5zsSCFo9bqKCr8bx15LeYBiT9&currencies={target}&base_currency={source}"
    res = requests.get(url)
    res.raise_for_status()  # Raise error if bad response
    data = res.json()
    print("API Response:", data)
    return data["data"][target]

@app.post("/")
async def receive_data(req: Request):
    data = await req.json()
    
    try:
        unit_currency = data["queryResult"]["parameters"]["unit-currency"][0]
        source_currency = unit_currency["currency"]
        amount = unit_currency["amount"]
        target_currency = data["queryResult"]["parameters"]["currency-name"][0]

        # Get the conversion factor
        rate = fetch_conversion_factor(source_currency, target_currency)
        converted_amount = amount * rate

        print(f"Converting {amount} {source_currency} to {target_currency} = {converted_amount:.2f}")

        return {
            "fulfillmentText": f"{amount} {source_currency} is approximately {converted_amount:.2f} {target_currency}"
        }

    except Exception as e:
        print("Error:", e)
        return {
            "fulfillmentText": "Sorry, there was a problem processing your request."
        }