import requests
import json
import time

SERVER_URL = "http://localhost:8000"

def test_license_system():
    print("[TEST] Starting License System Verification...")

    # 1. Generate a Key
    print("\n[1] Generating a new key...")
    try:
        resp = requests.post(f"{SERVER_URL}/admin/generate", json={"days_valid": 30, "count": 1, "memo": "TestUser"}, timeout=5)
        if resp.status_code != 200:
            print(f"[FAIL] Generation Failed: {resp.text}")
            return
        
        key_info = resp.json()[0]
        new_key = key_info['key']
        print(f"[OK] Key Generated: {new_key}")
    except Exception as e:
        print(f"[FAIL] Server Error: {e}")
        return

    # 2. Activate on Machine A (HWID_A)
    hwid_a = "AA:BB:CC:DD:EE:01"
    print(f"\n[2] Activating on Machine A ({hwid_a})...")
    resp = requests.post(f"{SERVER_URL}/api/activate", json={"key": new_key, "hwid": hwid_a})
    if resp.status_code == 200:
        print("[OK] Activation Successful (Expected)")
    else:
        print(f"[FAIL] Activation Failed: {resp.text}")

    # 3. Validate on Machine A
    print(f"\n[3] Validating on Machine A ({hwid_a})...")
    resp = requests.post(f"{SERVER_URL}/api/validate", json={"key": new_key, "hwid": hwid_a})
    data = resp.json()
    if data['valid']:
        print(f"[OK] Validation Passed (Expected). Remaining: {data['remaining_days']} days")
    else:
        print(f"[FAIL] Validation Failed: {data['message']}")

    # 4. Attempt Activate on Machine B (HWID_B) - SHOULD FAIL
    hwid_b = "FF:EE:DD:CC:BB:99"
    print(f"\n[4] Attempting Activation on Machine B ({hwid_b})...")
    resp = requests.post(f"{SERVER_URL}/api/activate", json={"key": new_key, "hwid": hwid_b})
    if resp.status_code != 200:
        print(f"[OK] Blocked Successfully (Expected): {resp.json().get('detail')}")
    else:
        print("[FAIL] Security Breach! Machine B was allowed to activate.")

    # 5. Attempt Validate on Machine B - SHOULD FAIL
    print(f"\n[5] Attempting Validation on Machine B ({hwid_b})...")
    resp = requests.post(f"{SERVER_URL}/api/validate", json={"key": new_key, "hwid": hwid_b})
    data = resp.json()
    if not data['valid']:
        print(f"[OK] Access Denied (Expected): {data['message']}")
    else:
        print("[FAIL] Security Breach! Machine B was valid.")

if __name__ == "__main__":
    test_license_system()
