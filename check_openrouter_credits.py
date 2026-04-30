"""
check_openrouter_credits.py — Script to check remaining credits for an OpenRouter API key.
Usage: python check_openrouter_credits.py
Requires: OPENROUTER_API_KEY in .env file or environment.
"""

import os
import requests
from pathlib import Path

def check_credits():
    # 1. Try to load from .env if it exists
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    os.environ["OPENROUTER_API_KEY"] = line.split("=", 1)[1].strip()

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in .env or environment variables.")
        return

    print("Checking OpenRouter credits...")
    
    try:
        # OpenRouter's auth key endpoint provides credit information
        response = requests.get(
            url="https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract balance information
            # Note: OpenRouter balance is returned in USD
            credit_info = data.get("data", {})
            label = credit_info.get("label", "Primary Key")
            usage = credit_info.get("usage", 0)
            limit = credit_info.get("limit") # limit can be null for pay-as-you-go
            
            # The 'usage' returned here is often cumulative. 
            # For exact 'balance', OpenRouter might return it differently for Org vs Personal keys.
            print("-" * 30)
            print(f"Key Label: {label}")
            print(f"Total Usage (USD): ${usage:.4f}")
            if limit:
                print(f"Credit Limit (USD): ${limit:.2f}")
                print(f"Remaining (Est): ${limit - usage:.4f}")
            else:
                print("Credit Limit: Unlimited (Pay-as-you-go)")
            print("-" * 30)
        else:
            print(f"Error: Received status code {response.status_code} from OpenRouter.")
            print(f"Message: {response.text}")

    except Exception as e:
        print(f"An error occurred while checking credits: {e}")

if __name__ == "__main__":
    check_credits()
