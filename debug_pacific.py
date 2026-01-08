import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def debug_pacific():
    # 1. Get Disruptions
    try:
        resp = requests.get(f"{BASE_URL}/disruptions")
        disruptions = resp.json()
    except Exception as e:
        print(f"Error fetching disruptions: {e}")
        return

    pacific = next((d for d in disruptions if "Pacific" in d['location'] or "Pacific" in d['type']), None)
    
    if not pacific:
        print("❌ 'Pacific Shipping Lane' disruption not found.")
        return

    print(f"✅ Found Disruption: {pacific['location']} (ID: {pacific['id']})")
    print(f"   Type: {pacific['type']}")

    # 2. Try to generate tickets
    print(f"\nAttempting to generate tickets for {pacific['id']}...")
    payload = {
        "disruption_id": pacific['id'],
        "allow_reroute": True,
        "max_cost_increase_percent": 20.0,
        "prioritize_high_priority": True,
        "additional_notes": "Debug test for Pacific"
    }
    
    try:
        # Note: The endpoint might be /tickets/{id} [POST] based on main.py
        url = f"{BASE_URL}/tickets/{pacific['id']}"
        resp = requests.post(url, json=payload)
        
        if resp.status_code == 200:
            tickets = resp.json()
            print(f"✅ API Call Successful. Status: {resp.status_code}")
            print(f"   Tickets Generated: {len(tickets)}")
            if len(tickets) == 0:
                print("   ⚠️  WARNING: 0 tickets were generated. This implies 'impact analysis' found 0 affected shipments.")
        else:
            print(f"❌ API Call Failed. Status: {resp.status_code}")
            print(f"   Response: {resp.text}")
            
    except Exception as e:
        print(f"Error calling ticket API: {e}")

if __name__ == "__main__":
    debug_pacific()
