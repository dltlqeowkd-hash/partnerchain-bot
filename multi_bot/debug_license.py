import requests
import os

# 현재 저장된 키 확인
license_file = "license.dat"
if os.path.exists(license_file):
    with open(license_file, "r") as f:
        key = f.read().strip()
    print(f"현재 저장된 키: {key}")
else:
    print("저장된 키가 없습니다.")
    exit()

# 서버에 검증 요청
import uuid
import re
mac_num = uuid.getnode()
mac = ':'.join(re.findall('..', '%012x' % mac_num))
hwid = mac.upper()

print(f"하드웨어 ID: {hwid}")

try:
    resp = requests.post("http://localhost:8000/api/validate", 
                        json={"key": key, "hwid": hwid}, 
                        timeout=5)
    
    print(f"\n서버 응답 상태: {resp.status_code}")
    data = resp.json()
    
    print("\n=== 서버가 반환한 전체 데이터 ===")
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print("\n=== 개별 필드 확인 ===")
    print(f"valid: {data.get('valid')}")
    print(f"message: {data.get('message')}")
    print(f"remaining_days: {data.get('remaining_days')}")
    print(f"memo: {repr(data.get('memo'))}")  # repr로 실제 값 확인
    print(f"expiration_date: {data.get('expiration_date')}")
    
except Exception as e:
    print(f"오류 발생: {e}")
