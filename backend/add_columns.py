"""
Railway PostgreSQL 데이터베이스에 컬럼 추가하는 스크립트
"""
from sqlalchemy import create_engine, text

# Railway PostgreSQL URL (올바른 비밀번호 사용)
DATABASE_URL = "postgresql://postgres:usmDMlNCNwjUWKmoORAIpOYqFbStzPEW@shinkansen.proxy.rlwy.net:47059/railway"

engine = create_engine(DATABASE_URL)

sql = """
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS trial_days INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS trial_start_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS trial_end_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) DEFAULT 'trial';
"""

try:
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("Success! Database columns added!")
except Exception as e:
    print(f"Error: {e}")
