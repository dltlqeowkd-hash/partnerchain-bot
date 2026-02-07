"""
자동 업데이트 모듈
- 서버에서 최신 버전 확인
- 필요 시 자동 다운로드
- 파일명 규칙: 프로그램명_날짜.exe
"""

import requests
import os
import sys
from datetime import datetime
from tkinter import messagebox, Tk
import subprocess

# 현재 클라이언트 버전 (빌드 시 자동 업데이트)
CLIENT_VERSION = "1.0.0"

def get_api_url():
    """
    API URL 가져오기 (config 파일 또는 환경 변수)
    """
    # 1. 환경 변수에서 읽기
    api_url = os.getenv("API_URL")
    
    # 2. config 파일에서 읽기
    if not api_url:
        config_path = "bot_config.json"
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    api_url = config.get("api_url", config.get("server_url"))
            except Exception as e:
                print(f"Config 읽기 오류: {e}")
    
    # 3. 기본값
    return api_url or "http://localhost:8000"

def check_for_updates():
    """
    서버에 최신 버전 확인 요청
    Returns:
        dict: 업데이트 정보 또는 None (오류 발생 시)
    """
    api_url = get_api_url()
    
    try:
        print(f"[UPDATE] 버전 체크 중... (현재: v{CLIENT_VERSION})")
        response = requests.get(
            f"{api_url}/api/version/check",
            params={"client_version": CLIENT_VERSION},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[UPDATE] 서버 최신 버전: v{data['current_version']}")
            return data
        else:
            print(f"[UPDATE] 버전 체크 실패: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"[UPDATE] 서버 응답 시간 초과 (오프라인 모드)")
        return None
    except Exception as e:
        print(f"[UPDATE] 버전 체크 오류 (오프라인 모드): {e}")
        return None

def prompt_update(update_info):
    """
    업데이트 다운로드 여부를 사용자에게 확인
    
    Args:
        update_info (dict): check_for_updates()에서 반환된 정보
    
    Returns:
        bool: 사용자가 다운로드를 선택했으면 True
    """
    root = Tk()
    root.withdraw()
    
    message = f"""새 버전이 출시되었습니다!

현재 버전: v{CLIENT_VERSION}
최신 버전: v{update_info['current_version']}
출시일: {update_info['release_date']}

변경사항:
{update_info['changelog']}

지금 다운로드하시겠습니까?
(다운로드 후 프로그램 재시작 필요)
"""
    
    user_choice = messagebox.askyesno("업데이트 알림", message)
    root.destroy()
    
    return user_choice

def download_update(download_url, new_version):
    """
    새 버전 다운로드 및 저장
    
    Args:
        download_url (str): 다운로드 URL
        new_version (str): 새 버전 번호
    
    Returns:
        str: 저장된 파일 경로 또는 None (실패 시)
    """
    try:
        # 현재 EXE가 있는 디렉토리 찾기
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 경우
            current_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # Python 스크립트로 실행 중인 경우
            current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 파일명 생성: NaverBot_v1.0.5_20260207.exe
        today = datetime.now().strftime("%Y%m%d")
        filename = f"NaverBot_v{new_version}_{today}.exe"
        save_path = os.path.join(current_dir, filename)
        
        print(f"[UPDATE] 다운로드 시작: {download_url}")
        print(f"[UPDATE] 저장 위치: {save_path}")
        
        # 스트리밍 다운로드 (대용량 파일에도 안전)
        response = requests.get(download_url, stream=True, timeout=60)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 진행률 표시
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r[UPDATE] 진행률: {progress:.1f}%", end='')
            
            print(f"\n[UPDATE] ✅ 다운로드 완료: {save_path}")
            return save_path
        else:
            print(f"[UPDATE] ❌ 다운로드 실패: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[UPDATE] ❌ 다운로드 오류: {e}")
        return None

def show_update_complete(file_path):
    """
    다운로드 완료 메시지 표시
    
    Args:
        file_path (str): 다운로드된 파일 경로
    """
    root = Tk()
    root.withdraw()
    
    messagebox.showinfo(
        "다운로드 완료",
        f"새 버전이 다운로드되었습니다!\n\n"
        f"파일 위치:\n{file_path}\n\n"
        f"현재 프로그램을 종료한 후\n"
        f"새 버전을 실행해주세요."
    )
    
    root.destroy()

def auto_update_check():
    """
    자동 업데이트 체크 메인 함수
    - 버전 확인
    - 업데이트 필요 시 사용자에게 알림
    - 다운로드 진행
    
    Returns:
        bool: 업데이트가 진행되었으면 True
    """
    update_info = check_for_updates()
    
    if not update_info:
        # 서버 연결 실패 또는 오류 (오프라인 모드로 계속)
        return False
    
    if update_info.get("force_update"):
        # 업데이트 필요
        if prompt_update(update_info):
            # 사용자가 다운로드를 선택함
            download_url = update_info["download_url"]
            new_version = update_info["current_version"]
            
            downloaded_path = download_update(download_url, new_version)
            
            if downloaded_path:
                show_update_complete(downloaded_path)
                return True
            else:
                # 다운로드 실패
                root = Tk()
                root.withdraw()
                messagebox.showerror(
                    "다운로드 실패",
                    "업데이트 다운로드에 실패했습니다.\n"
                    "인터넷 연결을 확인하고 다시 시도해주세요."
                )
                root.destroy()
                return False
        else:
            # 사용자가 다운로드를 거부함
            root = Tk()
            root.withdraw()
            messagebox.showwarning(
                "업데이트 건너뛰기",
                "최신 버전으로 업데이트하지 않으면\n"
                "일부 기능이 제한되거나 오류가 발생할 수 있습니다."
            )
            root.destroy()
            return False
    else:
        # 최신 버전 사용 중
        print(f"[UPDATE] ✅ 최신 버전입니다 (v{CLIENT_VERSION})")
        return False
