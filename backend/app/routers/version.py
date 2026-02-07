from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

router = APIRouter(prefix="/api/version", tags=["version"])

# 환경 변수에서 현재 버전 정보 읽기
CURRENT_VERSION = os.getenv("CURRENT_VERSION", "1.0.0")
RELEASE_DATE = os.getenv("RELEASE_DATE", "2026-02-07")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "partnerchain-releases")

class VersionCheckRequest(BaseModel):
    client_version: str

class VersionResponse(BaseModel):
    current_version: str
    release_date: str
    download_url: str
    changelog: str
    force_update: bool
    file_size_mb: Optional[float] = None

class DownloadResponse(BaseModel):
    download_url: str
    version: str
    expires_at: Optional[str] = None

def compare_versions(v1: str, v2: str) -> int:
    """
    버전 비교 함수
    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    try:
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        # 길이를 맞춤 (예: 1.0 vs 1.0.0)
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    except Exception:
        # 파싱 실패 시 문자열 비교
        return -1 if v1 < v2 else (0 if v1 == v2 else 1)

@router.get("/check", response_model=VersionResponse)
async def check_version(client_version: str = Query(..., description="클라이언트 현재 버전 (예: 1.0.3)")):
    """
    클라이언트 버전 체크 및 최신 버전 정보 반환
    
    Parameters:
    - client_version: 클라이언트가 보낸 현재 버전
    
    Returns:
    - current_version: 서버의 최신 버전
    - release_date: 최신 버전 출시일
    - download_url: EXE 다운로드 URL
    - changelog: 변경 사항 요약
    - force_update: 업데이트 필요 여부
    """
    is_outdated = compare_versions(client_version, CURRENT_VERSION) < 0
    
    # Cloudflare R2 Public URL 생성
    # 형식: https://pub-{account_id}.r2.dev/{bucket_name}/NaverBot_v{version}.exe
    if R2_ACCOUNT_ID:
        download_url = f"https://pub-{R2_ACCOUNT_ID}.r2.dev/{R2_BUCKET_NAME}/NaverBot_v{CURRENT_VERSION}.exe"
    else:
        # 개발 환경: 로컬 파일 또는 다른 호스팅
        download_url = f"http://localhost:8000/downloads/NaverBot_v{CURRENT_VERSION}.exe"
    
    # 실제 환경에서는 DB에서 changelog를 가져와야 함
    changelog = """
    [주요 변경사항]
    - 성능 최적화 및 버그 수정
    - 안정성 개선
    - 새로운 기능 추가
    """.strip()
    
    return VersionResponse(
        current_version=CURRENT_VERSION,
        release_date=RELEASE_DATE,
        download_url=download_url,
        changelog=changelog,
        force_update=is_outdated,
        file_size_mb=45.3  # 실제로는 S3에서 가져와야 함
    )

@router.get("/download/{version}", response_model=DownloadResponse)
async def get_download_url(version: str):
    """
    특정 버전의 다운로드 URL 반환
    
    Parameters:
    - version: 요청하는 버전 (예: 1.0.5)
    
    Returns:
    - download_url: 해당 버전의 다운로드 URL
    """
    # 보안: 버전 형식 검증 (예: 1.0.0)
    import re
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise HTTPException(status_code=400, detail="Invalid version format. Expected: X.Y.Z")
    
    # Cloudflare R2 URL 생성
    if R2_ACCOUNT_ID:
        download_url = f"https://pub-{R2_ACCOUNT_ID}.r2.dev/{R2_BUCKET_NAME}/NaverBot_v{version}.exe"
    else:
        download_url = f"http://localhost:8000/downloads/NaverBot_v{version}.exe"
    
    return DownloadResponse(
        download_url=download_url,
        version=version,
        expires_at=None  # Presigned URL 사용 시 만료 시간 포함
    )

@router.get("/latest")
async def get_latest_version():
    """
    최신 버전 정보만 간단히 반환 (Quick check용)
    """
    return {
        "version": CURRENT_VERSION,
        "release_date": RELEASE_DATE
    }
