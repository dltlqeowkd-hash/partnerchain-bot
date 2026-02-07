import PyInstaller.__main__
import os
import shutil

def build():
    print("Building Company Version (No-Auth)...")
    
    # Options for PyInstaller
    # Dynamic paths to avoid locks
    ts = int(__import__("time").time())
    work_dir = f'build_company_{ts}'
    dist_dir_name = f'dist_{ts}'
    
    opts = [
        'company_launcher.py',
        '--name=NaverShoppingBot_Company',
        '--onedir',
        '--noconsole',
        '--clean',
        '--noconfirm',
        f'--workpath={work_dir}',
        f'--distpath={dist_dir_name}', 
        '--add-data=bot_config.json;.',
        '--add-data=LICENSE.chromedriver;.',
    ]
    
    PyInstaller.__main__.run(opts)

    print("\n" + "="*50)
    print(" Build Complete!")
    print(" Reorganizing files into '최종ver/회사용'...")
    print("="*50)

    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, dist_dir_name) # Update to use dynamic dist 
    final_dir = os.path.join(base_dir, '최종ver')
    company_dir = os.path.join(final_dir, '회사용')

    # 1. Clean previous Company Folder
    if os.path.exists(company_dir):
        shutil.rmtree(company_dir)
    os.makedirs(company_dir)

    # 2. Move Bot Folder
    # PyInstaller created 'dist/NaverShoppingBot_Company' (from --name)
    bot_src = os.path.join(dist_dir, 'NaverShoppingBot_Company')
    bot_dst = os.path.join(company_dir, 'NaverShoppingBot')
    
    # Retry logic for copying
    import time
    for i in range(3):
        try:
            if os.path.exists(bot_dst):
                # Rename old folder instead of delete to avoid lock
                try:
                    os.rename(bot_dst, bot_dst + f"_old_{int(time.time())}")
                except:
                    shutil.rmtree(bot_dst)
            
            shutil.copytree(bot_src, bot_dst)
            break
        except Exception as e:
            print(f"Copy failed (attempt {i+1}): {e}")
            time.sleep(2)

    # 3. Create User Manual for Company
    manual_content = """
[네이버 쇼핑 봇 (회사용) 사용자 가이드]

본 버전은 인증 절차 없이 즉시 실행 가능한 회사 전용 버전입니다.

1. 프로그램 실행
   - 'NaverShoppingBot' 폴더 안에 있는 'company_launcher.exe' (또는 NaverShoppingBot.exe)를 실행하세요.
   * 참고: 실행 파일 이름은 빌드 설정에 따라 다를 수 있으나, 아이콘이 있는 실행 파일을 찾으시면 됩니다.

2. 설정 변경
   - 'bot_config.json' 파일을 메모장으로 열어 검색 키워드 및 설정을 변경할 수 있습니다.

3. 주의사항
   - 본 프로그램은 오프라인으로 동작하며 서버 연결을 하지 않습니다.
   - 외부 유출 시 누구나 사용할 수 있으므로 보안에 주의해주세요.
"""
    with open(os.path.join(company_dir, '사용설명서.txt'), 'w', encoding='utf-8') as f:
        f.write(manual_content.strip())

    print(f" Organization Complete!")
    print(f" Output Location: {company_dir}")
    print("="*50)

if __name__ == "__main__":
    build()
