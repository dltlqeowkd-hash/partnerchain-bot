import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import threading
import sys

import json
import os
from random_data import GENERIC_KEYWORDS

# 상수 - 경로 설정 (Portable)
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우 (exe 실행 위치 기준)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 파이썬 스크립트 실행 경우
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- LICENSE CHECK START ---
# 봇 실행 전 라이선스 체크 (1PC - 1Key 강제)
try:
    from license_check import check_license
    if not check_license():
        print("License verification failed. Exiting.")
        sys.exit(1)
except ImportError:
    # license_check.py 가 없을 경우 (개발 환경 등)
    print("Warning: license_check.py not found. Skipping check.")
    pass
# --- LICENSE CHECK END ---

from webdriver_manager.chrome import ChromeDriverManager
# Webdriver Manager will handle the driver path

DEBUGNER_PORT = 9222
DEBUGGER_ADDRESS = f"127.0.0.1:{DEBUGNER_PORT}"
CONFIG_FILE = os.path.join(BASE_DIR, 'bot_config.json')

class ConfigManager:
    @staticmethod
    def load():
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "min_time_min": 2,
                "max_time_min": 3,
                "mode": "PC",
                "smart_schedule": True,
                "include_ads": True,
                "max_pages": 3,
                "targets": [],
                "delays": {
                    "search_delay_min": 500,
                    "search_delay_max": 1000,
                    "scroll_delay_min": 800,
                    "scroll_delay_max": 2500,
                    "click_delay_min": 1000,
                    "click_delay_max": 2000
                }
            }
            ConfigManager.save(default_config)
            return default_config
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save(data):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

# 시각화 스크립트 (마우스 커서/터치 및 궤적 표시)
VISUAL_JS = """
// 커서/터치 포인터 생성
if (!document.getElementById('bot-cursor')) {
    let cursor = document.createElement('div');
    cursor.id = 'bot-cursor';
    cursor.style.position = 'absolute';
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.background = 'rgba(255, 0, 0, 0.7)'; // 붉은 반투명
    cursor.style.borderRadius = '50%';
    cursor.style.zIndex = '999999';
    cursor.style.pointerEvents = 'none'; // 클릭 방해 금지
    cursor.style.transition = 'all 0.05s linear';
    document.body.appendChild(cursor);
    
    // 궤적 컨테이너
    let trail = document.createElement('div');
    trail.id = 'bot-trail-container';
    trail.style.position = 'absolute';
    trail.style.top = '0';
    trail.style.left = '0';
    trail.style.width = '100%';
    trail.style.height = '100%';
    trail.style.pointerEvents = 'none';
    trail.style.zIndex = '999998';
    document.body.appendChild(trail);
}

window.moveBotCursor = function(x, y, isMobile) {
    let cursor = document.getElementById('bot-cursor');
    if (cursor) {
        cursor.style.left = (x - 10) + 'px';
        cursor.style.top = (y - 10) + 'px';
        cursor.style.background = isMobile ? 'rgba(0, 150, 255, 0.5)' : 'rgba(255, 50, 50, 0.5)'; // 모바일:파랑, PC:빨강
        
        // 궤적 남기기
        let dot = document.createElement('div');
        dot.style.position = 'absolute';
        dot.style.left = (x - 2) + 'px';
        dot.style.top = (y - 2) + 'px';
        dot.style.width = '4px';
        dot.style.height = '4px';
        dot.style.background = cursor.style.background;
        dot.style.borderRadius = '50%';
        dot.style.opacity = '0.3';
        document.getElementById('bot-trail-container').appendChild(dot);
    }
};

window.clearBotTrail = function() {
    let container = document.getElementById('bot-trail-container');
    if (container) container.innerHTML = '';
};
"""

class NaturalMouse:
    def __init__(self, driver):
        self.driver = driver
        self.action = ActionChains(driver)
        # JS 주입
        try:
            self.driver.execute_script(VISUAL_JS)
        except: pass

    def get_element_center(self, element):
        loc = element.location
        size = element.size
        return loc['x'] + size['width'] / 2, loc['y'] + size['height'] / 2

    def bezier_curve(self, start, end, control, t):
        # 2차 베지에 곡선 공식
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        return (x, y)

    def smooth_move_to(self, element):
        try:
            # 시각화 JS 재주입 (페이지 이동 시 초기화되므로)
            self.driver.execute_script(VISUAL_JS)
            self.driver.execute_script("window.clearBotTrail();") # 이전 궤적 삭제

            # 현재 마우스 위치 가정 (정확히 알 수 없으므로 화면 중앙이나 랜덤 시작)
            # 여기서는 편의상 요소 근처나 랜덤 위치에서 시작
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 500)
            
            end_x, end_y = self.get_element_center(element)
            
            # 제어점 (Control Point) 생성 - 곡선 효과
            control_x = random.randint(min(start_x, int(end_x)), max(start_x, int(end_x)))
            control_y = random.randint(min(start_y, int(end_y)), max(start_y, int(end_y)))
            
            steps = random.randint(15, 25)
            for i in range(steps + 1):
                t = i / steps
                x, y = self.bezier_curve((start_x, start_y), (end_x, end_y), (control_x, control_y), t)
                
                # 1. 시각화 (JS로 그리기)
                is_mobile = False # 기본값
                try: 
                    # 현재 모바일 모드인지 확인 (driver capabilities 등 활용 가능하지만 여기선 대략적)
                    is_mobile = self.driver.execute_script("return window.navigator.userAgent.includes('Mobile')")
                except: pass
                
                self.driver.execute_script(f"window.moveBotCursor({x}, {y}, {'true' if is_mobile else 'false'});")
                
                # 2. 실제 마우스 이동 (ActionChains는 상대좌표라 복잡하므로 여기선 시각화 위주로 가고 마지막에 진짜 이동)
                time.sleep(random.uniform(0.01, 0.03))
            
            # 마지막에 진짜 Selenium 이동 수행
            self.action.move_to_element(element).perform()
            time.sleep(0.2)
            
        except Exception as e:
            # 에러 나면 그냥 이동
            try: self.action.move_to_element(element).perform()
            except: pass

class BotLogic:
    def __init__(self, log_func, config, on_success=None):
        self.log = log_func
        self.config = config
        self.on_success = on_success
        self.driver = None
        self.mouse = None
        self.is_running = False
        self.current_mode = "PC" 

    def get_delay(self, key_prefix):
        d = self.config['delays']
        min_ms = d.get(f"{key_prefix}_min", 1000)
        max_ms = d.get(f"{key_prefix}_max", 2000)
        return random.randint(min_ms, max_ms) / 1000.0

    def apply_mobile_emulation(self):
        if self.current_mode == "Mobile":
            try:
                mobile_ua = "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G991N) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36"
                self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": mobile_ua})
                metrics = {"width": 360, "height": 800, "deviceScaleFactor": 3, "mobile": True, "touch": True}
                self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", metrics)
                self.driver.execute_script(VISUAL_JS)
            except: pass

    def setup_driver(self, mode_setting):
        try:
            if self.driver:
                try: self.driver.quit()
                except: pass
            
            if mode_setting == "Random":
                self.current_mode = random.choice(["PC", "Mobile"])
            else:
                self.current_mode = mode_setting
            
            self.log(f"브라우저 시작 모드: {self.current_mode}")

            options = Options()
            options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Auto-install/update driver matching the installed Chrome version
            # Modified for Offline/Company usage: Check local first
            local_driver = os.path.join(BASE_DIR, "chromedriver.exe")
            if os.path.exists(local_driver):
                driver_path = local_driver
                self.log(f"로컬 드라이버 사용: {driver_path}")
            else:
                try:
                    driver_path = ChromeDriverManager().install()
                except Exception as e:
                    self.log("드라이버 다운로드 실패 (인터넷 확인 필요)")
                    raise e
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            if self.current_mode == "Mobile":
                self.driver.set_window_size(450, 900) # 모바일 창 크기
                self.apply_mobile_emulation()
                self.log("모바일 에뮬레이션 모드 적용 완료.")
            else:
                self.driver.set_window_size(1920, 1080) # PC 창 크기 복구
                self.driver.maximize_window()
                self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ""})
                self.driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
            
            self.mouse = NaturalMouse(self.driver)
            return True
        except Exception as e:
            self.log(f"드라이버 연결 실패: {e}")
            return False

    def human_typing(self, element, text):
        try:
            element.click()
            time.sleep(0.5)
            
            # 기존 텍스트 지우기 (한 글자씩 백스페이스로 지우는 척 하거나 Ctrl+A)
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.1)
            element.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)
            
            # 진짜 한 글자씩 타이핑
            for char in text:
                element.send_keys(char)
                # 타자 속도 변화 (중간중간 멈칫)
                delay = random.uniform(0.1, 0.3)
                if random.random() < 0.1: delay += 0.3
                time.sleep(delay)
                
            time.sleep(self.get_delay("search_delay"))
        except:
            # 실패 시에도 한글자씩 시도
            try: 
                for char in text:
                    element.send_keys(char)
                    time.sleep(0.1)
            except: pass

    def human_scroll(self, max_scrolls=None):
        try:
            scrolls = 0
            while True:
                if max_scrolls and scrolls >= max_scrolls: break
                scroll_amount = random.randint(300, 700)
                self.driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
                time.sleep(self.get_delay("scroll_delay"))
                if random.random() < 0.2:
                    self.driver.execute_script(f"window.scrollBy({{top: -100, behavior: 'smooth'}});")
                    time.sleep(0.5)
                height = self.driver.execute_script("return document.body.scrollHeight")
                curr = self.driver.execute_script("return window.scrollY + window.innerHeight")
                if curr >= height: break
                scrolls += 1
                if random.random() > 0.9: break
        except: pass

    def check_and_switch_tab(self):
        try:
            handles = self.driver.window_handles
            if len(handles) > 1:
                new_tab = handles[-1]
                if self.driver.current_window_handle != new_tab:
                    self.driver.switch_to.window(new_tab)
                    self.log("새 탭 감지됨. 전환 완료.")
                    time.sleep(1)
                    if self.current_mode == "Mobile":
                        self.apply_mobile_emulation()
                        self.driver.refresh()
                        time.sleep(2)
            return True
        except:
            return False

    def get_schedule_multiplier(self):
        """현재 시간대에 따른 대기 시간 배율 (스마트 스케줄)"""
        if not self.config.get("smart_schedule", False):
            return 1.0
        
        hour = time.localtime().tm_hour
        # 00~06시: 수면 시간 (활동 매우 적음, 3배 느리게)
        if 0 <= hour < 7: return 4.0
        # 07~09시: 출근 시간 (조금 느리게)
        if 7 <= hour < 10: return 1.5
        # 10~18시: 일과 시간 (정상)
        if 10 <= hour < 19: return 1.0
        # 19~23시: 퇴근/저녁 (활발, 0.8배 빠르게)
        if 19 <= hour < 24: return 0.8
        
        return 1.0

    def calculate_cycle_time(self, min_t, max_t):
        base = random.randint(min_t * 60, max_t * 60)
        mult = self.get_schedule_multiplier()
        final = int(base * mult)
        self.log(f"스마트 스케줄 적용: {mult}배 (다음 사이클 대기: {final}초)")
        return final

    def find_target_on_page(self, t_id, include_ads):
        """현재 페이지에서 타겟 ID 찾기 (광고 필터링 포함)"""
        # ID로 요소 찾기 (href나 data-id 포함)
        xpath = f"//*[contains(@href,'{t_id}')] | //*[contains(@data-id,'{t_id}')]"
        elements = self.driver.find_elements(By.XPATH, xpath)
        
        for el in elements:
            if not el.is_displayed(): continue
            
            # 광고 체크
            is_ad = False
            try:
                # 상위 요소들을 뒤져서 '광고' 뱃지가 있는지 확인 (네이버 쇼핑 구조에 따라 다름)
                parent = el.find_element(By.XPATH, "./../../..") # 대략적 상위
                if "광고" in parent.text:
                    is_ad = True
            except: pass
            
            if is_ad and not include_ads:
                self.log(f"타겟({t_id})을 찾았으나 '광고'이므로 건너뜁니다.")
                continue
                
            return el
        return None

    def go_to_next_page(self, page_num):
        """다음 페이지로 이동 시도"""
        try:
            self.log(f"{page_num}페이지로 이동 시도...")
            
            # 1. 숫자 클릭 시도
            try:
                next_btn = self.driver.find_element(By.XPATH, f"//a[text()='{page_num}']")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass

            # 2. '다음' 버튼 시도
            try:
                next_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '다음')]")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass
            
            return False
        except:
            return False

    def run_cycle_loop(self, targets, min_t, max_t, mode_setting):
        while self.is_running:
            try:
                # 사이클 시간 계산 (스케줄러 반영)
                cycle_duration = self.calculate_cycle_time(min_t, max_t)
                start_time = time.time()
                
                self.log(f"=== 사이클 시작 ({self.current_mode} / {cycle_duration}초) ===")

                if not self.setup_driver(mode_setting):
                    time.sleep(5)
                    continue

                target = random.choice(targets)
                t_kw1 = target['keyword']    # 1차 키워드
                t_kw2 = target.get('keyword_2', '') # 2차 키워드 (없을 수도 있음)
                t_id = target['id']
                
                max_pages = self.config.get('max_pages', 3)
                include_ads = self.config.get('include_ads', True)

                wait = WebDriverWait(self.driver, 10)

                # 1. 예열 (다음/네이트)
                portal = random.choice(["https://www.daum.net", "https://www.nate.com"])
                self.driver.get(portal)
                time.sleep(2)
                
                # 랜덤 포털 검색
                for _ in range(2):
                    if not self.is_running: break
                    kw = random.choice(GENERIC_KEYWORDS)
                    self.log(f"[예열] 검색: {kw}")
                    try:
                        search = None
                        if "daum" in portal:
                            try: search = self.driver.find_element(By.ID, "q") 
                            except: search = self.driver.find_element(By.NAME, "q")
                        else: 
                            try: search = self.driver.find_element(By.ID, "q")
                            except: search = self.driver.find_element(By.NAME, "q")

                        if search:
                            self.human_typing(search, kw)
                            search.send_keys(Keys.RETURN)
                            time.sleep(2)
                            self.check_and_switch_tab()
                            self.human_scroll(max_scrolls=2)
                            try:
                                links = self.driver.find_elements(By.TAG_NAME, "a")
                                valid_links = [l for l in links if l.is_displayed() and len(l.text) > 4]
                                if valid_links:
                                    l = random.choice(valid_links[:8])
                                    l.click()
                                    time.sleep(self.get_delay("click_delay"))
                                    self.check_and_switch_tab()
                                    self.human_scroll(max_scrolls=1)
                                    if len(self.driver.window_handles) > 1:
                                        self.driver.close()
                                        self.driver.switch_to.window(self.driver.window_handles[0])
                                    else:
                                        self.driver.back()
                            except: pass
                    except: pass
                
                # 2. 메인 전 예열 (네이버 메인 - 랜덤)
                if self.is_running:
                    self.log("[네이버 예열] 네이버 메인 이동")
                    self.driver.get("https://www.naver.com")
                    time.sleep(2)
                    
                    for _ in range(random.randint(1, 2)):
                        if not self.is_running: break
                        kw = random.choice(GENERIC_KEYWORDS)
                        self.log(f"[네이버 예열] 랜덤 검색: {kw}")
                        try:
                            s_box = None
                            if self.current_mode == "Mobile":
                                try:
                                    self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click()
                                    time.sleep(1)
                                except: pass
                                s_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                            else:
                                s_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                            
                            self.human_typing(s_box, kw)
                            s_box.send_keys(Keys.RETURN)
                            time.sleep(2)
                            
                            self.check_and_switch_tab()
                            self.human_scroll(max_scrolls=2)
                            
                            # 다시 메인으로
                            self.driver.get("https://www.naver.com")
                            time.sleep(2)
                        except:
                            self.driver.get("https://www.naver.com")
                            time.sleep(2)

                # 3. 메인 타겟 로직 함수
                def search_and_find(input_kw):
                    self.log(f"네이버 메인 이동 후 검색: {input_kw}")
                    self.driver.get("https://www.naver.com")
                    time.sleep(2)
                    
                    # 1. 메인 검색창 찾기 & 검색
                    try:
                        search_box = None
                        if self.current_mode == "Mobile":
                            # 모바일: 가짜검색창 -> 진짜검색창
                            try:
                                self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click()
                                time.sleep(1)
                            except: pass
                            search_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                        else:
                            # PC
                            search_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                        
                        self.human_typing(search_box, input_kw)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(2)
                    except:
                        # 실패 시 쇼핑검색 URL로 Fallback (어쩔 수 없음)
                        self.log("메인 검색 실패, URL로 이동 시도")
                        self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")
                        time.sleep(2)
                    
                    self.check_and_switch_tab()
                    
                    # 2. 쇼핑 탭 클릭
                    # 2. [변경] 쇼핑 탭 클릭 대신 -> 스크롤 후 '가격비교 더보기' 상세 진입
                    found_more = False
                    try:
                        self.log("메인 검색 후 '네이버 가격비교 더보기' 찾는 중...")
                        # 충분히 로딩되도록 스크롤
                        for _ in range(4):
                           self.human_scroll(max_scrolls=1)
                           time.sleep(1)
                           
                           # '가격비교 더보기' 또는 '쇼핑 더보기' 찾기
                           btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '가격비교 더보기') or contains(text(), '쇼핑 더보기')]")
                           for b in btns:
                               if b.is_displayed():
                                   self.mouse.smooth_move_to(b)
                                   b.click()
                                   found_more = True
                                   break
                           if found_more: break
                    except: pass
                    
                    if not found_more:
                        self.log("더보기 버튼을 찾지 못해 쇼핑탭 URL로 이동합니다.")
                        # Fallback
                        self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")

                        
                    self.check_and_switch_tab()
                    time.sleep(2)
                    
                    # 페이지 탐색 루프
                    for p in range(1, max_pages + 1):
                        self.log(f"현재 {p}페이지 탐색 중...")
                        
                        # 스크롤 
                        self.human_scroll(max_scrolls=3)
                        
                        # 찾기
                        el = self.find_target_on_page(t_id, include_ads)
                        if el:
                            self.log("타겟 발견! 클릭.")
                            self.mouse.smooth_move_to(el)
                            
                            cur_h = len(self.driver.window_handles)
                            try: el.click()
                            except: self.driver.execute_script("arguments[0].click()", el)
                            
                            time.sleep(2)
                            if len(self.driver.window_handles) > cur_h:
                                self.driver.switch_to.window(self.driver.window_handles[-1])
                                if self.current_mode == "Mobile":
                                    self.apply_mobile_emulation()
                                    self.driver.refresh()
                                    time.sleep(2)
                            return True
                        
                        # 못 찾았으면 다음 페이지
                        if p < max_pages:
                            if not self.go_to_next_page(p + 1):
                                self.log("다음 페이지 버튼을 찾을 수 없습니다.")
                                break
                            time.sleep(3)
                            
                    return False

                # 1차 시도
                success = search_and_find(t_kw1)
                
                # 실패 시 2차 시도
                if not success and t_kw2:
                    self.log(f"1차 키워드 실패. 2차 키워드({t_kw2}) 시도...")
                    success = search_and_find(t_kw2)
                
                if success:
                    self.log("상세 페이지 진입 성공. 정밀 인터랙션 시작.")
                    
                    # 성공 카운트 증가
                    if self.on_success:
                        self.on_success(t_id)

                    interaction_start = time.time()
                    
                    # 1. [신규] 갤러리/썸네일 구경 (초반 시선 끌기)
                    try:
                        self.log("갤러리 이미지 탐색...")
                        thumbs = self.driver.find_elements(By.CSS_SELECTOR, "div.mask_thumb_list, div.image_thumb_list, .product_images img") # 일반적인 썸네일 클래스들
                        if thumbs:
                            limit = min(len(thumbs), 5)
                            for i in range(limit):
                                if not self.is_running: break
                                try:
                                    self.mouse.smooth_move_to(thumbs[i])
                                    thumbs[i].click() # 썸네일 클릭해서 메인 이미지 바꾸기
                                    time.sleep(random.uniform(1.5, 3.0))
                                except: pass
                    except: pass

                    # 2. 상세정보 펼쳐보기 (필수)
                    try:
                        time.sleep(1)
                        expand_btn = self.driver.find_element(By.XPATH, "//*[contains(text(), '펼쳐보기') or contains(text(), '상품정보 더보기')]")
                        self.mouse.smooth_move_to(expand_btn)
                        expand_btn.click()
                        self.log("상세정보 더보기 클릭 완료")
                        time.sleep(1)
                    except: pass
                    
                    # 3. [신규] 옵션 선택 시뮬레이션 (구매 의도 강력 신호)
                    try:
                        self.log("옵션 선택 시뮬레이션...")
                        # 1) 옵션 버튼/박스 찾기
                        opt_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '옵션') or contains(@class, 'option')] | //div[contains(@class, 'Option_option')]") 
                        self.mouse.smooth_move_to(opt_btn)
                        opt_btn.click() # 옵션 열기
                        time.sleep(random.uniform(1.0, 2.0))
                        
                        # 2) 아무 옵션이나 하나 슬쩍 마우스 올리거나 클릭 시도 (선택 후 취소)
                        opts = self.driver.find_elements(By.TAG_NAME, "li")
                        if opts:
                           target_opt = random.choice(opts[:5]) # 상위 몇개 중 하나
                           self.mouse.smooth_move_to(target_opt)
                           time.sleep(0.5)
                           # 클릭은 안하거나, 클릭 후 닫기 등 (복잡도 줄이기 위해 마우스 오버만)
                        
                        # 3) 다른 곳 클릭해서 닫기 (body 등)
                        ActionChains(self.driver).move_by_offset(50, 50).click().perform()
                        time.sleep(1)
                    except: pass

                    # 4. 정독(Deep Read) 스크롤링 & 텍스트 하이라이팅
                    while time.time() - start_time < cycle_duration:
                        if not self.is_running: break
                        
                        remain_time = cycle_duration - (time.time() - start_time)
                        if remain_time < 0: break
                        
                        self.log(f"체류 유지 중... (남은 시간: {int(remain_time)}초)")
                        
                        # 랜덤 행동 정의
                        actions = ["scroll_slow", "highlight_text", "review_read", "qna_read"]
                        actions = ["scroll_slow", "highlight_text", "review_read", "qna_read"]
                        weights = [40, 20, 20, 20] # Q&A 비중 증가
                        
                        # 가끔 찜/장바구니 (로그인 유도) - 확률 매우 낮춤 (10%)
                        if random.random() < 0.1: 
                            actions.append("wish_cart")
                            weights.append(5) 
                            
                        act = random.choices(actions, weights=weights, k=1)[0]
                        
                        try:
                            if act == "scroll_slow":
                                # 천천히 읽듯이 스크롤
                                for _ in range(random.randint(3, 6)):
                                    self.driver.execute_script(f"window.scrollBy({{top: {random.randint(100, 300)}, behavior: 'smooth'}});")
                                    time.sleep(random.uniform(1.0, 3.0))
                                    
                            elif act == "highlight_text":
                                # 텍스트 드래그 흉내 (설명글 근처)
                                try:
                                    # 본문 텍스트 찾기 시도
                                    desc = self.driver.find_element(By.CSS_SELECTOR, "div.se-main-container, .detail_detail_area")
                                    self.mouse.smooth_move_to(desc)
                                    # ActionChains로 드래그
                                    ActionChains(self.driver).click_and_hold(desc).move_by_offset(random.randint(10, 50), random.randint(0, 10)).release().perform()
                                    time.sleep(1)
                                except: pass
                                
                            elif act == "review_read":
                                btn = self.driver.find_element(By.XPATH, "//*[contains(text(), '리뷰') or contains(text(), '구매평')]")
                                self.mouse.smooth_move_to(btn)
                                btn.click()
                                time.sleep(random.uniform(3, 6)) # 리뷰 읽는 시간

                            elif act == "qna_read":
                                # [신규] Q&A 탭 클릭 -> 질문 클릭 -> 읽기 -> 닫기
                                try:
                                    btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Q&A') or contains(text(), '문의')]")
                                    self.mouse.smooth_move_to(btn)
                                    btn.click()
                                    time.sleep(2)
                                    
                                    # 질문 목록 찾기 (네이버 쇼핑 일반적 구조)
                                    qna_items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='question'], li[class*='question'], a[class*='product_qna']")
                                    # 광고/공지 제외하고 실제 질문처럼 보이는 것
                                    valid_qnas = [q for q in qna_items if q.is_displayed()]
                                    
                                    if valid_qnas:
                                        target_q = random.choice(valid_qnas[:4]) # 상위 4개 중 하나
                                        self.mouse.smooth_move_to(target_q)
                                        target_q.click()
                                        self.log("다른 구매자의 Q&A를 읽는 중...")
                                        time.sleep(random.uniform(3, 5)) # 읽기
                                        
                                        # 다시 클릭해서 닫거나 다른 영역 클릭
                                        target_q.click()
                                        time.sleep(1)
                                except: pass
                                
                            elif act == "wish_cart":
                                # 찜하기/장바구니 - 로그인 팝업 뜰 수 있음
                                btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '찜') or contains(text(), '장바구니')]")
                                if btns:
                                    b = random.choice(btns)
                                    self.mouse.smooth_move_to(b)
                                    self.log("구매 시그널(찜/장바구니) 클릭 시도")
                                    b.click()
                                    time.sleep(2)
                                    # 혹시 로그인 팝업 뜨면 닫기 시도 (X버튼 찾기는 어려우므로 그냥 ESC나 뒤로가기)
                                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

                        except: pass
                        
                        time.sleep(random.randint(2, 4))
                else:
                    self.log("최종적으로 상품을 찾지 못했습니다.")

                # 정리
                self.driver.delete_all_cookies()
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            except Exception as e:
                self.log(f"Critical Error: {e}")
                time.sleep(5)

class DelaySettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("딜레이 설정 (ms 단위)")
        self.config = config
        self.result = None
        
        self.entries = {}
        row = 0
        keys = ["search_delay", "scroll_delay", "click_delay"]
        labels = ["검색 타이핑 간격", "스크롤 대기 시간", "클릭 후 대기 시간"]
        
        for k, label in zip(keys, labels):
            tk.Label(self, text=label).grid(row=row, column=0, padx=5, pady=5)
            
            f = tk.Frame(self)
            f.grid(row=row, column=1)
            
            e_min = tk.Entry(f, width=8)
            e_min.insert(0, str(config['delays'].get(f"{k}_min", 1000)))
            e_min.pack(side="left")
            
            tk.Label(f, text="~").pack(side="left")
            
            e_max = tk.Entry(f, width=8)
            e_max.insert(0, str(config['delays'].get(f"{k}_max", 2000)))
            e_max.pack(side="left")
            
            self.entries[k] = (e_min, e_max)
            row += 1
            
        btn = tk.Button(self, text="저장", command=self.save)
        btn.grid(row=row, column=0, columnspan=2, pady=10)

    def save(self):
        new_delays = {}
        try:
            for k, (emn, emx) in self.entries.items():
                new_delays[f"{k}_min"] = int(emn.get())
                new_delays[f"{k}_max"] = int(emx.get())
            self.config['delays'] = new_delays
            ConfigManager.save(self.config)
            messagebox.showinfo("저장", "설정이 저장되었습니다.")
            self.destroy()
        except ValueError:
            messagebox.showerror("오류", "숫자만 입력하세요.")

class BotApp:
    def __init__(self, root, expiration_date=None):
        self.root = root
        title = "네이버 쇼핑 봇 v3.0 (스케줄러/2차키워드/광고제어)"
        if expiration_date:
            title += f" - [사용 기한: {expiration_date}]"
        
        self.root.title(title)
        self.root.geometry("700x850")
        
        # 만료일 표시 라벨
        if expiration_date:
            lb_exp = tk.Label(self.root, text=f"라이센스 만료일: {expiration_date}", fg="blue", font=("Arial", 11, "bold"))
            lb_exp.pack(side="top", fill="x", pady=5)
        
        self.config = ConfigManager.load()
        self.logic = BotLogic(self.log, self.config, self.on_success_ui)
        self.create_ui()

    def create_ui(self):
        # 1. 기본 설정 (상단)
        f_top = tk.LabelFrame(self.root, text="기본 설정")
        f_top.pack(fill="x", padx=10, pady=5)
        
        tk.Label(f_top, text="Min(분):").pack(side="left")
        self.e_min = tk.Entry(f_top, width=4)
        self.e_min.insert(0, self.config.get("min_time_min", 3))
        self.e_min.pack(side="left", padx=2)
        
        tk.Label(f_top, text="Max(분):").pack(side="left")
        self.e_max = tk.Entry(f_top, width=4)
        self.e_max.insert(0, self.config.get("max_time_min", 5))
        self.e_max.pack(side="left", padx=2)
        
        tk.Label(f_top, text="| 모드:").pack(side="left", padx=5)
        self.combo_mode = ttk.Combobox(f_top, values=["PC", "Mobile", "Random"], width=7, state="readonly")
        self.combo_mode.set(self.config.get("mode", "PC"))
        self.combo_mode.pack(side="left")
        
        # 고급 옵션 (체크박스)
        self.var_smart = tk.BooleanVar(value=self.config.get("smart_schedule", True))
        self.var_ads = tk.BooleanVar(value=self.config.get("include_ads", True))
        
        tk.Checkbutton(f_top, text="스마트 스케줄", variable=self.var_smart).pack(side="left", padx=5)
        tk.Checkbutton(f_top, text="광고 포함", variable=self.var_ads).pack(side="left", padx=5)

        tk.Label(f_top, text="| 최대페이지:").pack(side="left")
        self.e_page = tk.Entry(f_top, width=3)
        self.e_page.insert(0, self.config.get("max_pages", 3))
        self.e_page.pack(side="left")

        tk.Button(f_top, text="상세 딜레이", command=self.open_settings).pack(side="right", padx=5)

        # 2. 타겟 관리
        f_list = tk.LabelFrame(self.root, text="타겟 키워드 관리 (1차 -> 실패시 2차)")
        f_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        f_in = tk.Frame(f_list)
        f_in.pack(fill="x")
        
        tk.Label(f_in, text="1차 키워드:").grid(row=0, column=0)
        self.e_kw1 = tk.Entry(f_in, width=15)
        self.e_kw1.grid(row=0, column=1)
        
        tk.Label(f_in, text="2차 키워드(옵션):").grid(row=0, column=2)
        self.e_kw2 = tk.Entry(f_in, width=15)
        self.e_kw2.grid(row=0, column=3)
        
        tk.Label(f_in, text="상품ID:").grid(row=0, column=4)
        self.e_id = tk.Entry(f_in, width=10)
        self.e_id.grid(row=0, column=5)
        
        tk.Button(f_in, text="추가", command=self.add_item).grid(row=0, column=6, padx=5)
        tk.Button(f_in, text="수정", command=self.update_item).grid(row=0, column=7, padx=5)
        tk.Button(f_in, text="삭제", command=self.del_item).grid(row=0, column=8, padx=5)
        
        self.tree = ttk.Treeview(f_list, columns=("k1", "k2", "id", "cnt"), show="headings", height=8)
        self.tree.heading("k1", text="1차 키워드")
        self.tree.heading("k2", text="2차 키워드")
        self.tree.heading("id", text="상품 ID")
        self.tree.heading("cnt", text="성공")
        self.tree.column("k1", width=140)
        self.tree.column("k2", width=140)
        self.tree.column("id", width=90)
        self.tree.column("cnt", width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Load
        for t in self.config.get("targets", []):
            k2 = t.get("keyword_2", "")
            cnt = t.get("success_count", 0)
            self.tree.insert("", "end", values=(t['keyword'], k2, t['id'], cnt))

        # 3. 로그 및 실행
        btn_start = tk.Button(self.root, text="START / STOP (설정 자동 저장)", command=self.toggle_start, bg="#4CAF50", fg="white", font=("Bold", 12))
        btn_start.pack(fill="x", padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self.root, height=12)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)

    def open_settings(self):
        DelaySettingsDialog(self.root, self.config)

    def save_current_state(self):
        try:
            self.config["min_time_min"] = int(self.e_min.get())
            self.config["max_time_min"] = int(self.e_max.get())
            self.config["mode"] = self.combo_mode.get()
            self.config["smart_schedule"] = self.var_smart.get()
            self.config["include_ads"] = self.var_ads.get()
            self.config["max_pages"] = int(self.e_page.get())
            

            targets = []
            for item in self.tree.get_children():
                vals = self.tree.item(item)['values']
                targets.append({
                    "keyword": str(vals[0]),
                    "keyword_2": str(vals[1]) if vals[1] != "None" else "",
                    "id": str(vals[2]),
                    "success_count": int(vals[3]) if len(vals) > 3 else 0
                })
            self.config["targets"] = targets
            ConfigManager.save(self.config)
        except Exception as e:
            print(f"Save Error: {e}")

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        try:
            item = self.tree.item(selected_items[0])
            vals = item['values']
            # vals = (k1, k2, id, count)
            
            # Clear entries
            self.e_kw1.delete(0, tk.END)
            self.e_kw2.delete(0, tk.END)
            self.e_id.delete(0, tk.END)
            
            # Insert values
            self.e_kw1.insert(0, vals[0])
            if len(vals) > 1 and vals[1] and str(vals[1]) != "None":
                self.e_kw2.insert(0, vals[1])
            if len(vals) > 2:
                self.e_id.insert(0, vals[2])
        except Exception as e:
            print(f"Selection Error: {e}")

    def update_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
             messagebox.showwarning("경고", "수정할 항목을 선택하세요.")
             return
        
        item_id = selected_items[0]
        k1, k2, i = self.e_kw1.get(), self.e_kw2.get(), self.e_id.get()
        
        if k1 and i:
            # 기존 success_count 유지
            try:
                old_vals = self.tree.item(item_id)['values']
                cnt = old_vals[3] if len(old_vals) > 3 else 0
                
                self.tree.item(item_id, values=(k1, k2, i, cnt))
                self.save_current_state()
                
                # Clear fields
                self.e_kw1.delete(0, tk.END)
                self.e_kw2.delete(0, tk.END)
                self.e_id.delete(0, tk.END)
                
                # Selection 해제
                self.tree.selection_remove(item_id)
                messagebox.showinfo("성공", "수정되었습니다.")
            except Exception as e:
                print(f"Update Error: {e}")
        else:
            messagebox.showwarning("경고", "1차 키워드와 상품ID는 필수입니다.")

    def add_item(self):
        k1, k2, i = self.e_kw1.get(), self.e_kw2.get(), self.e_id.get()
        if k1 and i:
            self.tree.insert("", "end", values=(k1, k2, i, 0))
            self.save_current_state()
            # Clear fields
            self.e_kw1.delete(0, tk.END)
            self.e_kw2.delete(0, tk.END)
            self.e_id.delete(0, tk.END)

    def del_item(self):
        for i in self.tree.selection():
            self.tree.delete(i)
        self.save_current_state()

    def toggle_start(self):
        if self.logic.is_running:
            self.logic.is_running = False
            self.log("중단 요청...")
        else:
            self.save_current_state()
            self.logic.is_running = True
            
            min_t = int(self.e_min.get())
            max_t = int(self.e_max.get())
            mode = self.combo_mode.get()
            targets = self.config["targets"]
            
            if not targets:
                messagebox.showerror("Err", "타겟이 없습니다.")
                return

            threading.Thread(target=self.logic.run_cycle_loop, args=(targets, min_t, max_t, mode), daemon=True).start()

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def on_success_ui(self, target_id):
        self.root.after(0, lambda: self._update_count(target_id))

    def _update_count(self, target_id):
        for item in self.tree.get_children():
            vals = self.tree.item(item)['values']
            if str(vals[2]) == str(target_id):
                current_cnt = int(vals[3]) if len(vals) > 3 else 0
                new_cnt = current_cnt + 1
                self.tree.item(item, values=(vals[0], vals[1], vals[2], new_cnt))
                self.save_current_state()
                self.log(f"타겟({target_id}) 성공 횟수 증가: {new_cnt}회")
                break

def main(expiration_date=None):
    try:
        root = tk.Tk()
        app = BotApp(root, expiration_date)
        root.mainloop()
    except Exception as e:
        print(f"UI Error: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()

