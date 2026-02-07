import requests
import sys

SERVER_URL = "http://localhost:8000"

def test_flow():
    print("1. Admin Login...")
    try:
        auth = requests.post(f"{SERVER_URL}/token", data={"username": "debug_admin", "password": "password123"})
        if auth.status_code != 200:
            print(f"FAILED: Login error {auth.text}")
            return
        token = auth.json()["access_token"]
        print("   OK")
    except Exception as e:
        print(f"FAILED: Server not reachable? {e}")
        return

    print("2. Generate Key (valid for 5 days)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        gen = requests.post(f"{SERVER_URL}/admin/generate_keys", json={"days_valid": 5, "count": 1, "memo": "Verif Test"}, headers=headers)
        if gen.status_code != 200:
            print(f"FAILED: Gen error {gen.text}")
            return
        key_info = gen.json()[0]
        key = key_info["key_string"]
        exp = key_info["expires_at"]
        print(f"   OK -> Key: {key}, Expires: {exp}")
    except Exception as e:
        print(f"FAILED: {e}")
        return

    print("3. Verify Key (Client Side)...")
    try:
        hwid = "TEST_HWID_12345"
        ver = requests.post(f"{SERVER_URL}/verify", json={"key_string": key, "hwid": hwid})
        data = ver.json()
        
        if data["valid"]:
            print(f"   OK -> Verified! Expiration from server: {data['expires_at']}")
            if str(data['expires_at'])[:10] == str(exp)[:10]:
                 print("   SUCCESS! Dates match.")
            else:
                 print(f"   WARNING: Date mismatch? Server sent {data['expires_at']}")
        else:
            print(f"FAILED: Verification returned invalid. {data}")
            return
    except Exception as e:
        print(f"FAILED: {e}")
        return
        
    print("\nALL TESTS PASSED.")

if __name__ == "__main__":
    test_flow()
