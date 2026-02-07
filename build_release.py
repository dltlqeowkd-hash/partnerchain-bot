import PyInstaller.__main__
import os

def build():
    print("Building Commercial Release...")
    
    # Options for PyInstaller
    opts = [
        'launcher.py',               # Main script
        '--name=NaverShoppingBot_v3', # Exe name
        '--onedir',                  # Create a directory (easier for debugging & config)
        '--noconsole',               # Hide console window (GUI only)
        '--clean',                   # Clean cache
        '--noconfirm',               # Overwrite output directory without asking
        '--add-data=bot_config.json;.', # Include config file
        '--add-data=LICENSE.chromedriver;.',
        # '--icon=icon.ico',         # Add icon if you have one
    ]
    
    PyInstaller.__main__.run(opts)
    
    print("\n" + "="*50)
    print(" Building Admin Tool...")
    print("="*50)
    
    # Options for Admin Tool
    admin_opts = [
        'simple_admin.py',
        '--name=KeyGenerator',
        '--onefile', # Single exe for admin is easier
        '--noconsole',
        '--noconfirm',
        '--clean'
    ]
    PyInstaller.__main__.run(admin_opts)

    print("\n" + "="*50)
    print(" Build Complete!")
    print(" Reorganizing files into '최종ver'...")
    print("="*50)

    import shutil

    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, 'dist')
    final_dir = os.path.join(base_dir, '최종ver')
    
    admin_dir = os.path.join(final_dir, '관리자용')
    user_dir = os.path.join(final_dir, '사용자용')

    # 1. Clean previous FinalVersion
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    os.makedirs(admin_dir)
    os.makedirs(user_dir)

    # 2. Setup Admin Folder
    # Move KeyGenerator
    shutil.copy2(os.path.join(dist_dir, 'KeyGenerator.exe'), os.path.join(admin_dir, 'KeyGenerator.exe'))
    
    # Copy License Server (Source Code) - Admin needs to run this
    server_src = os.path.join(base_dir, 'license_server')
    server_dst = os.path.join(admin_dir, 'license_server')
    shutil.copytree(server_src, server_dst)
    
    # Remove __pycache__ from copied server to keep it clean
    for root, dirs, files in os.walk(server_dst):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
    
    # Copy Admin Tool Source (Optional, but user wanted "files needed for work")
    # Actually, user said "files to work at company", so maybe the source checks out?
    # For now, just the executable and server is safest for "Admin Tools". 
    # But user specifically said "files to work at company", implyng development?
    # "Admin tools (Key gen), necessary files to work at company, etc"
    # I will just put the server and the exe for now to keep it clean.
    
    # 3. Setup User Folder
    # Move Bot Folder
    bot_src = os.path.join(dist_dir, 'NaverShoppingBot_v3')
    bot_dst = os.path.join(user_dir, 'NaverShoppingBot')
    
    # Also copy to Admin Folder for testing
    admin_bot_dst = os.path.join(admin_dir, 'NaverShoppingBot')
    shutil.copytree(bot_src, admin_bot_dst)

    # Move to User Folder (using copytree again to have two copies)
    shutil.copytree(bot_src, bot_dst)

    # Create User Manual
    manual_content = """
[네이버 쇼핑 봇 사용자 가이드]

1. 프로그램 실행
   - 'NaverShoppingBot' 폴더 안에 있는 'launcher.exe' (또는 launcher)를 실행하세요.

2. 라이선스 인증
   - 관리자로부터 받은 시리얼 키를 입력하고 'Login & Start'를 누르세요.
   - 최초 1회 인증 시 현재 컴퓨터(PC)에 라이선스가 귀속됩니다.
   - 다른 컴퓨터에서는 동일한 키를 사용할 수 없습니다.

3. 사용 방법
   - 봇이 실행되면 키워드와 상품 ID를 확인하고 작업을 시작하세요.
   - 모든 데이터는 안전하게 저장됩니다.

4. 문의
   - 프로그램 사용 중 문제가 발생하면 관리자에게 문의해주세요.
"""
    with open(os.path.join(user_dir, '사용설명서.txt'), 'w', encoding='utf-8') as f:
        f.write(manual_content.strip())

    print(f" Organization Complete!")
    print(f" Output Location: {final_dir}")
    print("="*50)

if __name__ == "__main__":
    build()
