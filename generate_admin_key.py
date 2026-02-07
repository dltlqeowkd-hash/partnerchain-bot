import requests

SERVER_URL = "http://localhost:8000"

def generate_key():
    # 1. Login (Auto-creates admin on first run)
    login_data = {"username": "debug_admin", "password": "password123"}
    try:
        response = requests.post(f"{SERVER_URL}/token", data=login_data)
        if response.status_code != 200:
            print("Login failed:", response.text)
            return
        
        token = response.json()["access_token"]
        
        # 2. Generate Key
        headers = {"Authorization": f"Bearer {token}"}
        key_data = {
            "days_valid": 30,
            "count": 1,
            "memo": "Test Key for User"
        }
        
        response = requests.post(f"{SERVER_URL}/admin/generate_keys", json=key_data, headers=headers)
        if response.status_code == 200:
            key_info = response.json()[0]
            print("\n" + "="*40)
            print(" [SUCCESS] New License Key Generated!")
            print(f" Key: {key_info['key_string']}")
            print(f" Expires: {key_info['expires_at']}")
            print("="*40 + "\n")
        else:
            print("Key generation failed:", response.text)
            
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure the server is running on port 8000!")

if __name__ == "__main__":
    generate_key()
