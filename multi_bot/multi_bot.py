import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import requests # [추가] 서버 통신용
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
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
import os
import json
from random_data import GENERIC_KEYWORDS

# 상수 - 경로 설정 (Portable)
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우 (exe 실행 위치 기준)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 파이썬 스크립트 실행 경우
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- LICENSE CHECK START ---
# Main entry point handles license check now.
# --- LICENSE CHECK END ---

from webdriver_manager.chrome import ChromeDriverManager

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
                "mixed_mode": False,
                "max_pages": 3,
                "targets_shopping": [],
                "targets_blog": [],
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
if (!document.getElementById('bot-cursor')) {
    let cursor = document.createElement('div');
    cursor.id = 'bot-cursor';
    cursor.style.position = 'absolute';
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.background = 'rgba(255, 0, 0, 0.7)';
    cursor.style.borderRadius = '50%';
    cursor.style.zIndex = '999999';
    cursor.style.pointerEvents = 'none';
    cursor.style.transition = 'all 0.05s linear';
    cursor.style.top = '0px'; 
    cursor.style.left = '0px';
    document.body.appendChild(cursor);
    
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
        cursor.style.background = isMobile ? 'rgba(0, 150, 255, 0.5)' : 'rgba(255, 50, 50, 0.5)';
        
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
        try:
            self.driver.execute_script(VISUAL_JS)
        except: pass

    def get_element_center(self, element):
        loc = element.location
        size = element.size
        return loc['x'] + size['width'] / 2, loc['y'] + size['height'] / 2

    def bezier_curve(self, start, end, control, t):
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        return (x, y)

    def smooth_move_to(self, element):
        try:
            self.driver.execute_script(VISUAL_JS)
            self.driver.execute_script("window.clearBotTrail();")
            
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 500)
            end_x, end_y = self.get_element_center(element)
            
            control_x = random.randint(min(start_x, int(end_x)), max(start_x, int(end_x)))
            control_y = random.randint(min(start_y, int(end_y)), max(start_y, int(end_y)))
            
            steps = random.randint(15, 25)
            for i in range(steps + 1):
                t = i / steps
                x, y = self.bezier_curve((start_x, start_y), (end_x, end_y), (control_x, control_y), t)
                
                is_mobile = False
                try: is_mobile = self.driver.execute_script("return window.navigator.userAgent.includes('Mobile')")
                except: pass
                
                try: self.driver.execute_script(f"window.moveBotCursor({x}, {y}, {'true' if is_mobile else 'false'});")
                except: pass
                
                time.sleep(random.uniform(0.01, 0.03))
            
            self.action.move_to_element(element).perform()
            time.sleep(0.2)
        except:
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
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            if self.current_mode == "Mobile":
                self.driver.set_window_size(450, 900)
                self.apply_mobile_emulation()
                self.log("모바일 에뮬레이션 모드 적용 완료.")
            else:
                self.driver.set_window_size(1920, 1080)
                self.driver.maximize_window()
            
            self.mouse = NaturalMouse(self.driver)
            return True
        except Exception as e:
            self.log(f"드라이버 시작 실패: {e}")
            return False

    def human_typing(self, element, text):
        try:
            element.click()
            time.sleep(0.5)
            try:
                element.send_keys(Keys.CONTROL, 'a')
                time.sleep(0.1)
                element.send_keys(Keys.BACK_SPACE)
            except: pass
            time.sleep(0.5)
            for char in text:
                element.send_keys(char)
                delay = random.uniform(0.1, 0.3)
                if random.random() < 0.1: delay += 0.3
                time.sleep(delay)
            time.sleep(self.get_delay("search_delay"))
        except:
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

    def _timer_loop(self):
        while self.is_running:
            try:
                if hasattr(self, 'cycle_start_time') and hasattr(self, 'cycle_total_duration') and self.cycle_start_time:
                    elapsed = time.time() - self.cycle_start_time
                    remaining = int(self.cycle_total_duration - elapsed)
                    if remaining < 0: remaining = 0
                    self.update_timer_label(f"남은 시간: {remaining}초")
            except: pass
            time.sleep(1)

    def get_schedule_multiplier(self):
        if not self.config.get("smart_schedule", False): return 1.0
        hour = time.localtime().tm_hour
        if 0 <= hour < 7: return 1.5 # [변경] 4.0 -> 1.5 (테스트 용이성 및 과도한 지연 방지)
        if 7 <= hour < 10: return 1.2 # [변경] 1.5 -> 1.2
        if 10 <= hour < 19: return 1.0
        if 19 <= hour < 24: return 0.8
        return 1.0

    def calculate_cycle_time(self, min_t, max_t):
        base = random.randint(min_t * 60, max_t * 60)
        mult = self.get_schedule_multiplier()
        final = int(base * mult)
        if mult != 1.0:
            self.log(f"⚡ 스마트 스케줄 자동 조정: x{mult}배 (현재시간 반영) -> 최종 {final}초")
        return final

    def find_target_on_page(self, t_id, include_ads):
        xpath = f"//*[contains(@href,'{t_id}')] | //*[contains(@data-id,'{t_id}')]"
        elements = self.driver.find_elements(By.XPATH, xpath)
        for el in elements:
            if not el.is_displayed(): continue
            is_ad = False
            try:
                parent = el.find_element(By.XPATH, "./../../..")
                if "광고" in parent.text: is_ad = True
            except: pass
            if is_ad and not include_ads:
                self.log(f"타겟({t_id})을 찾았으나 '광고'이므로 건너뜁니다.")
                continue
            return el
        return None

    def go_to_next_page(self, page_num):
        try:
            self.log(f"{page_num}페이지로 이동 시도...")
            try:
                next_btn = self.driver.find_element(By.XPATH, f"//a[text()='{page_num}']")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass

            try:
                next_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '다음')]")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass
            return False
        except: return False

    def run_cycle_loop(self, min_t, max_t, mode_setting):
        threading.Thread(target=self._timer_loop, daemon=True).start()

        while self.is_running:
            try:
                work_plan = []
                if self.config.get("mixed_mode", False):
                    work_plan = ["shopping", "blog"]
                    self.log("🔄 사이클 시작: [쇼핑 + 블로그] 통합 모드")
                else:
                    work_type = self.config.get("work_type", "shopping")
                    work_plan = [work_type]
                    self.log(f"🔄 사이클 시작: [{work_type.upper()}] 단일 모드")

                for current_work in work_plan:
                    if not self.is_running: break
                    self.log(f">> 🚀 {current_work.upper()} 작업 시작")
                    
                    targets = self.config.get(f"targets_{current_work}", [])
                    if not targets:
                        self.log(f"⚠️ {current_work} 타겟이 없어 건너뜁니다.")
                        continue
                        
                    # 드라이버 셋업
                    if not self.setup_driver(mode_setting):
                        time.sleep(5)
                        continue
                    
                    # [NEW] 전체 사이클 목표 시간 계산 (MIN~MAX 범위)
                    cycle_duration = self.calculate_cycle_time(min_t, max_t)
                    cycle_start_time = time.time()
                    self.cycle_start_time = cycle_start_time
                    self.cycle_total_duration = cycle_duration
                    self.log(f"⏱️ 목표 사이클 시간: {int(cycle_duration)}초 ({cycle_duration/60:.1f}분)")
                    
                    target = random.choice(targets)
                    t_kw1 = target['keyword']    
                    t_kw2 = target.get('keyword_2', '')
                    t_id = target['id']
                    t_product_link = target.get('product_link', '')  # [추가] 판매링크 필드
                    
                    max_pages = self.config.get('max_pages', 3) 
                    include_ads = self.config.get('include_ads', True)
                    wait = WebDriverWait(self.driver, 10)

                    # [NEW] 예열 로직 시작 - DAUM/NATE (30초 ~ 1분 소요)
                    portal = random.choice(["https://www.daum.net", "https://www.nate.com"])
                    self.log(f"🔥 [예열] 브라우저 워밍업 시작 ({portal.split('//')[1]})")
                    try:
                        self.driver.get(portal)
                        time.sleep(2)
                        
                        # 간단한 검색어 입력 및 스크롤
                        warmup_kw = random.choice(GENERIC_KEYWORDS)
                        self.log(f"   - 검색어 입력: {warmup_kw}")
                        
                        search_box = None
                        if "daum" in portal:
                            try: search_box = self.driver.find_element(By.NAME, "q")
                            except: pass
                        else:
                            try: 
                                search_box = self.driver.find_element(By.ID, "q") # nate
                            except: 
                                try: search_box = self.driver.find_element(By.NAME, "q")
                                except: pass
                            
                        if search_box:
                            try:
                                # [수정] 상호작용 가능할 때까지 대기
                                wait_warmup = WebDriverWait(self.driver, 5)
                                if "daum" in portal:
                                    wait_warmup.until(EC.element_to_be_clickable((By.NAME, "q")))
                                else:
                                    try: wait_warmup.until(EC.element_to_be_clickable((By.ID, "q")))
                                    except: wait_warmup.until(EC.element_to_be_clickable((By.NAME, "q")))
                                    
                                self.human_typing(search_box, warmup_kw)
                                search_box.send_keys(Keys.RETURN)
                                time.sleep(2)
                                self.human_scroll(max_scrolls=2)
                                time.sleep(1)
                            except: pass # 예열 중 오류는 조용히 넘어감
                            
                        self.log("✅ 예열 완료. 네이버로 이동합니다.")
                    except Exception as e:
                        self.log(f"⚠️ 예열 중 오류 (무시하고 진행): {e}")

                    # [NEW] 예열 2단계 - 네이버 메인
                    if self.is_running:
                        self.log("[예열 2단계] 네이버 메인 접속")
                        self.driver.get("https://www.naver.com")
                        time.sleep(2)
                        
                        for _ in range(random.randint(1, 2)):
                            if not self.is_running:
                                self.log("⛔ 사용자가 중지 요청")
                                break
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
                                
                                self.human_typing(s_box, kw)
                                s_box.send_keys(Keys.RETURN)
                                time.sleep(2)
                                self.check_and_switch_tab()
                                self.human_scroll(max_scrolls=2)
                                self.driver.get("https://www.naver.com")
                                time.sleep(2)
                            except:
                                self.driver.get("https://www.naver.com")
                                time.sleep(2)
                    # [NEW] 예열 로직 종료

                    def search_and_find_shopping(input_kw):
                        self.log(f"[쇼핑] 검색: {input_kw}")
                        self.driver.get("https://www.naver.com")
                        time.sleep(2)
                        try:
                            search_box = None
                            if self.current_mode == "Mobile":
                                try: self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click(); time.sleep(1)
                                except: pass
                            search_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                            self.human_typing(search_box, input_kw)
                            search_box.send_keys(Keys.RETURN)
                            time.sleep(2)
                        except:
                            self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")
                            time.sleep(2)
                        
                        self.check_and_switch_tab()
                        found_more = False
                        try:
                            for _ in range(4):
                               self.human_scroll(max_scrolls=1)
                               time.sleep(1)
                               btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '가격비교 더보기') or contains(text(), '쇼핑 더보기')]")
                               for b in btns:
                                   if b.is_displayed():
                                       self.mouse.smooth_move_to(b); b.click(); found_more = True; break
                               if found_more: break
                        except: pass
                        if not found_more: self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")
                        self.check_and_switch_tab()
                        time.sleep(2)
                        
                        for p in range(1, max_pages + 1):
                            self.log(f"쇼핑 {p}페이지 탐색 중...")
                            self.human_scroll(max_scrolls=3)
                            el = self.find_target_on_page(t_id, include_ads)
                            if el:
                                self.log("타겟 발견! 클릭.")
                                self.mouse.smooth_move_to(el)
                                cur_h = len(self.driver.window_handles)
                                try: el.click()
                                except: self.driver.execute_script("arguments[0].click()", el)
                                time.sleep(3)
                                if len(self.driver.window_handles) > cur_h:
                                    self.driver.switch_to.window(self.driver.window_handles[-1])
                                    if self.current_mode == "Mobile":
                                        self.apply_mobile_emulation()
                                        self.driver.refresh()
                                        time.sleep(2)
                                return True
                            if p < max_pages:
                                if not self.go_to_next_page(p + 1): break
                                time.sleep(3)
                        return False

    
                    def search_and_find_blog(kw, target_kw_check, target_link_id, product_link="", is_retry=False):
                        mode_str = "2차(확정)" if is_retry else "1차(도전)"
                        self.log(f"[블로그] {mode_str} 시작 - 네이버 페이크 검색")
                        self.driver.get("https://www.naver.com")
                        time.sleep(2)
                        fake_count = random.randint(1, 3)
                        for _ in range(fake_count):
                            if not self.is_running: return False
                            fake_kw = random.choice(GENERIC_KEYWORDS)
                            try:
                                if self.current_mode == "Mobile": list(map(lambda x: x.click(), self.driver.find_elements(By.ID, "MM_SEARCH_FAKE")[:1]))
                                s_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                                self.human_typing(s_box, fake_kw)
                                s_box.send_keys(Keys.RETURN)
                                time.sleep(2)
                                self.human_scroll(max_scrolls=2)
                                time.sleep(1)
                                self.driver.get("https://www.naver.com")
                                time.sleep(2)
                            except: self.driver.get("https://www.naver.com"); time.sleep(2)

                        self.log(f"[블로그] {mode_str} 실제 검색: {kw}")
                        try:
                            if self.current_mode == "Mobile": list(map(lambda x: x.click(), self.driver.find_elements(By.ID, "MM_SEARCH_FAKE")[:1]))
                            s_box = wait.until(EC.element_to_be_clickable((By.ID, "query")))
                            self.human_typing(s_box, kw)
                            s_box.send_keys(Keys.RETURN)
                            time.sleep(2)
                        except: return False
                        self.check_and_switch_tab()
                        
                        # --- 내부 함수: 현재 화면에서 블로그 찾기 ---
                        def find_blog_post_and_click():
                            # [우선순위 1] href 기반 블로그 링크 직접 검색 (가장 정확)
                            # "검색결과 더보기" 클릭 후 페이지는 다른 HTML 구조 사용
                            # 어제 채팅 기록 참고: a[href*='blog.naver.com'] 방식이 가장 확실
                            blog_links = []
                            try:
                                # CSS Selector로 블로그 링크 직접 수집
                                blog_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='blog.naver.com']")
                                if blog_links:
                                    self.log(f"🔍 블로그 링크 검색 (href 기반)... {len(blog_links)}개 발견")
                            except: pass
                            
                            # [우선순위 2] 기존 XPath 방식 (일반 검색 페이지용 백업)
                            if not blog_links:
                                try:
                                    articles = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'bx')] | //li[contains(@class, 'sh_blog_top')] | //div[contains(@class, 'total_wrap')]")
                                    self.log(f"🔎 스캔 대상 게시글 수 (XPath): {len(articles)}")
                                except: articles = []
                            else:
                                articles = []  # href 기반 검색 성공 시 XPath는 건너뜀
                            
                            # href 기반 링크를 우선 처리
                            all_items = list(blog_links) + list(articles)
                            
                            valid_articles = []
                            for i, art in enumerate(all_items):
                                if not self.is_running: return False
                                try:
                                    text_content = art.text
                                    
                                    # [링크 추출]
                                    href = ""
                                    target_el = None
                                    try:
                                        # href 기반 검색인 경우 바로 가져오기
                                        if art in blog_links:
                                            href = art.get_attribute("href")
                                            target_el = art
                                        else:
                                            # 기존 방식 (여러 셀렉터 시도)
                                            try: target_el = art.find_element(By.CSS_SELECTOR, "a.api_txt_lines"); href = target_el.get_attribute("href")
                                            except: 
                                                try: target_el = art.find_element(By.CSS_SELECTOR, "a.total_tit"); href = target_el.get_attribute("href")
                                                except: 
                                                    try: target_el = art.find_element(By.CSS_SELECTOR, "a.title_link"); href = target_el.get_attribute("href")
                                                    except: 
                                                        try: target_el = art.find_element(By.CSS_SELECTOR, "a.link_tit"); href = target_el.get_attribute("href")
                                                        except: target_el = art.find_element(By.TAG_NAME, "a"); href = target_el.get_attribute("href")
                                    except: pass
                                    
                                    # [필터링] search.naver.com 링크는 무시 (정렬 버튼 등)
                                    if "search.naver.com" in href:
                                        continue

                                    # [DEBUG] 상세 로그 출력 (상위 10개만)
                                    if i < 10:
                                        preview = text_content[:20].replace('\n', ' ') if text_content else "(텍스트 없음)"
                                        self.log(f"   [{i}] {preview}... | Link: {href}")

                                    # [2] ID/식별자 매칭
                                    is_match = False
                                    
                                    # [2] ID/식별자 매칭
                                    is_match = False
                                    
                                    # 2-1. 텍스트 매칭
                                    if str(target_link_id) in text_content:
                                        is_match = True
                                        self.log(f"✅ ID 텍스트 매칭 성공! ({target_link_id})")
                                    
                                    # 2-2. URL/ID 매칭
                                    if not is_match and href:
                                        # (A) 단순 URL 포함 여부 (기존 방식 개선)
                                        # 쿼리 파라미터가 날라가는 문제 해결을 위해 ? 제거 로직 수정
                                        clean_target_base = str(target_link_id).replace("https://", "").replace("http://", "").replace("m.", "").replace("www.", "").strip('/')
                                        clean_href_body = href.replace("https://", "").replace("http://", "").replace("m.", "").replace("www.", "")
                                        
                                        if clean_target_base in clean_href_body:
                                            is_match = True
                                            self.log(f"✅ ID 링크 매칭 성공 (URL Contain)! \n   Target: {clean_target_base} \n   Href: {clean_href_body}")

                                        # (B) 블로그 글 번호(숫자 ID) 매칭 - 가장 강력한 방법
                                        if not is_match and "blog.naver.com" in str(target_link_id):
                                            try:
                                                import re
                                                # URL 끝의 숫자 추출 (예: .../22416444822 -> 22416444822)
                                                # PostView.naver?logNo=22416444822 대응
                                                
                                                # 1. 타겟 ID에서 숫자 추출
                                                target_nums = re.findall(r'\d+', str(target_link_id))
                                                if target_nums:
                                                    post_id = target_nums[-1] # 보통 마지막 숫자가 글 번호 (날짜 등 제외)
                                                    
                                                    # 글 번호가 10자리 이상인지 확인 (네이버 블로그 ID는 보통 길다)
                                                    if len(post_id) >= 10:
                                                        if post_id in href:
                                                            is_match = True
                                                            self.log(f"✅ ID 링크 매칭 성공 (Post ID)! ID: {post_id}")
                                            except: pass
                                    
                                    if is_match:
                                        self.log(f"✨ 타겟 발견! 진입 시도...")
                                        blog_clicked = False
                                        try:
                                            # 클릭할 요소 (제목 링크 권장)
                                            try: 
                                                if target_el and target_el.is_displayed():
                                                    click_el = target_el
                                                else:
                                                    click_el = art.find_element(By.TAG_NAME, "a")
                                            except: click_el = art
                                            
                                            self.mouse.smooth_move_to(click_el)
                                            time.sleep(random.uniform(1, 2))  # 마우스 이동 후 자연스러운 대기
                                            click_el.click()
                                            
                                            # 새 탭 전환
                                            time.sleep(random.uniform(2, 4))  # 페이지 로딩 대기 (자연스럽게)
                                            self.check_and_switch_tab()
                                            self.log(f"📄 현재 탭: {self.driver.title}")
                                            time.sleep(random.uniform(1, 2))  # 탭 전환 후 잠시 대기
                                            blog_clicked = True
                                        except Exception as e:
                                            self.log(f"❌ 클릭 실패: {e}")
                                            return False
                                        
                                        # 블로그 클릭 성공 → 내부 로직으로 진행 (naver.me 찾기)
                                        if blog_clicked:
                                            return True  # 일단 find_blog_post_and_click()에서는 True 반환
                                except Exception as e:
                                    # self.log(f"⚠️ 요소 분석 중 오류: {e}")
                                    pass
                            return False

                        # 1단계: 검색 직후 즉시 스캔 (상단 노출된 경우)
                        self.log("🔍 1차 스캔: 상단 노출 여부 확인...")
                        blog_found = find_blog_post_and_click()
                        
                        if not blog_found:
                            self.log("ℹ️ 상단에 없음. '검색결과 더보기' 시도...")

                            # 2단계: 자연스러운 스크롤로 '검색결과 더보기' 버튼 찾기
                            # [수정] Keys.END 대신 PAGE_DOWN으로 천천히 스크롤
                            self.log("📜 페이지를 천천히 스크롤하며 '더보기' 버튼 탐색...")
                            last_height = self.driver.execute_script("return document.body.scrollHeight")
                            scroll_count = 0
                            max_scrolls = 20  # 최대 20회 스크롤
                            
                            for i in range(max_scrolls):
                                 if not self.is_running: break
                                 try:
                                     # 천천히 PAGE_DOWN으로 스크롤 (자연스러운 동작)
                                     body = self.driver.find_element(By.TAG_NAME, "body")
                                     body.send_keys(Keys.PAGE_DOWN)
                                     scroll_count += 1
                                     time.sleep(random.uniform(0.3, 0.6))  # 랜덤 대기 (더 자연스럽게)
                                 except: pass
                                 
                                 # 페이지 끝 도달 확인
                                 try:
                                     new_height = self.driver.execute_script("return document.body.scrollHeight")
                                     if new_height == last_height:
                                         self.log(f"📜 페이지 끝 도달 (스크롤 {scroll_count}회)")
                                         break
                                     last_height = new_height
                                 except: break
                            
                            # '검색결과 더보기' 버튼 클릭 시도
                            found_more = False
                            xpath_list = ["//*[contains(text(), '검색결과 더보기')]", "//*[contains(text(), '뷰 더보기')]", "//a[contains(@class, 'more_content')]", "//*[contains(text(), 'VIEW 더보기')]"]
                            for xp in xpath_list:
                                try:
                                    btns = self.driver.find_elements(By.XPATH, xp)
                                    for btn in btns:
                                        if btn.is_displayed():
                                            self.log(f"✅ 더보기 버튼 발견 및 클릭: {btn.text}")
                                            self.mouse.smooth_move_to(btn)
                                            btn.click()
                                            time.sleep(3)
                                            found_more = True
                                            break
                                    if found_more: break
                                except: pass
                            
                            if not found_more:
                                self.log("ℹ️ 더보기 버튼 없음 (이미 마지막이거나 못찾음)")
                            else:
                                # [중요] 페이지 로딩 대기 추가 (JavaScript 동적 로딩 대응)
                                self.log("⏳ 페이지 콘텐츠 로딩 대기 중... (5초)")
                                time.sleep(5)
                                
                                # [중요] Lazy Loading 트리거 (스크롤로 동적 콘텐츠 강제 로드)
                                try:
                                    self.driver.execute_script("window.scrollTo(0, 500);")  # 아래로
                                    time.sleep(0.5)
                                    self.driver.execute_script("window.scrollTo(0, 0);")    # 다시 위로
                                    self.log("✅ Lazy Loading 트리거 완료")
                                except: pass

                            # 3단계: 전체 재스캔 (더보기 이후 로드된 게시글 포함)
                            self.log(f"🔎 2차 스캔: 전체 리스트에서 타겟 탐색 (2차: {target_kw_check}, ID: {target_link_id})")
                            blog_found = find_blog_post_and_click()
                        
                        # 블로그를 찾지 못한 경우
                        if not blog_found:
                            self.log("❌ 타겟 블로그를 찾지 못했습니다.")
                            return False

                        # ===== 블로그 내부 로직 시작 (blog_found = True일 때만 실행됨) =====
                        self.log("📖 블로그 진입. naver.me 링크 탐색 (천천히 스크롤)...")
                        
                        # iframe 전환 시도
                        is_iframe = False
                        try: 
                            self.driver.switch_to.frame("mainFrame")
                            is_iframe = True
                            self.log("✅ iframe 전환 완료")
                        except: 
                            self.log("ℹ️ iframe 없음, 현재 페이지에서 진행")
                        
                        # 천천히 스크롤하며 naver.me 링크 찾기
                        # [중요] 블로그 진입 직후 바로 클릭하면 티가 나므로, 최소 시간 동안 스크롤 보장
                        scroll_duration = random.randint(30, 60)
                        min_scroll_time = random.randint(15, 25)  # 최소 15~25초는 무조건 스크롤
                        self.log(f"⏱️ {scroll_duration}초간 천천히 스크롤하며 naver.me 링크 탐색 (최소 {min_scroll_time}초 읽기)...")
                        start_read = time.time()
                        found_target_link = None
                        link_found_time = None  # 링크 발견 시각 기록
                        
                        while time.time() - start_read < scroll_duration:
                            if not self.is_running: break
                            
                            elapsed = time.time() - start_read
                            
                            # 1. naver.me 링크 탐색 (찾아도 최소 시간 전에는 저장만)
                            # [중요] 블로그 자체 URL(blog.naver.com)은 제외하고, 실제 판매 링크(naver.me, smartstore 등)만 찾기
                            if not found_target_link:  # 아직 안 찾았으면 계속 탐색
                                try:
                                    links = self.driver.find_elements(By.TAG_NAME, "a")
                                    for l in links:
                                        href = l.get_attribute("href")
                                        if not href: continue
                                        
                                        # [필터링] 블로그 자체 링크 제외 (blog.naver.com, m.blog.naver.com)
                                        if "blog.naver.com" in href or "m.blog.naver.com" in href:
                                            continue
                                        
                                        # [우선순위 1] naver.me 패턴 (가장 일반적인 판매 링크)
                                        if "naver.me" in href:
                                            found_target_link = l
                                            link_found_time = time.time()
                                            self.log(f"🔍 판매 링크 발견! (naver.me) {href} - 자연스럽게 스크롤 계속...")
                                            break
                                        # [우선순위 2] 스마트스토어 직접 링크
                                        elif "smartstore.naver.com" in href:
                                            found_target_link = l
                                            link_found_time = time.time()
                                            self.log(f"🔍 판매 링크 발견! (스마트스토어) {href} - 자연스럽게 스크롤 계속...")
                                            break
                                        # [우선순위 3] 네이버 쇼핑 상품 링크
                                        elif "shopping.naver.com" in href and "/products/" in href:
                                            found_target_link = l
                                            link_found_time = time.time()
                                            self.log(f"🔍 판매 링크 발견! (쇼핑) {href} - 자연스럽게 스크롤 계속...")
                                            break
                                        # [우선순위 4] product_link 필드 값과 일치 (사용자 지정)
                                        elif product_link and product_link in href:
                                            found_target_link = l
                                            link_found_time = time.time()
                                            self.log(f"🔍 판매 링크 발견! (필드 매칭) {href} - 자연스럽게 스크롤 계속...")
                                            break
                                except: pass
                            
                            # 2. 최소 시간 경과 + 링크 발견 시 종료
                            if found_target_link and elapsed >= min_scroll_time:
                                self.log(f"✅ 최소 읽기 시간 충족 ({int(elapsed)}초). 판매 링크 클릭 준비...")
                                break
                            
                            # 3. 천천히 스크롤 (자연스럽게)
                            try:
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                for _ in range(random.randint(1, 3)):
                                    body.send_keys(Keys.ARROW_DOWN)
                                    time.sleep(0.2)
                            except: 
                                self.human_scroll(max_scrolls=1)
                            
                            time.sleep(random.uniform(1.0, 2.0))
                            
                        # naver.me 링크 발견 시 클릭 및 쇼핑 페이지 이동
                        if found_target_link:
                            self.log("🛒 판매 링크 클릭! 쇼핑 페이지로 이동...")
                            try:
                                self.mouse.smooth_move_to(found_target_link)
                                time.sleep(random.uniform(1, 2.5))  # 마우스 이동 후 자연스러운 대기
                                found_target_link.click()
                                if is_iframe: self.driver.switch_to.default_content()
                                time.sleep(random.uniform(2, 4))  # 페이지 로딩 대기 (자연스럽게)
                                self.check_and_switch_tab()
                                self.log("✅ 쇼핑 상세 페이지 진입 성공")
                                time.sleep(random.uniform(1, 2))  # 쇼핑 페이지 진입 후 잠시 관찰
                                return True
                            except Exception as e:
                                self.log(f"❌ 링크 클릭 실패: {e}")
                        else:
                            self.log("❌ 판매 링크(naver.me)를 찾지 못했습니다.")
                            
                        if is_iframe: self.driver.switch_to.default_content()
                        return False

                    success = False
                    if current_work == "shopping":
                        success = search_and_find_shopping(t_kw1)
                        if not success and t_kw2: success = search_and_find_shopping(t_kw2)
                    elif current_work == "blog":
                        success = search_and_find_blog(t_kw1, t_kw2, t_id, t_product_link, is_retry=False)
                        if not success and t_kw2: success = search_and_find_blog(t_kw2, t_kw2, t_id, t_product_link, is_retry=True)

                    if success:
                         self.log("🎉 타겟 작업 성공! 상세 액션 수행...")
                         if self.on_success: self.on_success(t_id)
                         
                         # 지금까지 사용한 시간 계산
                         elapsed_time = time.time() - cycle_start_time
                         remaining_time = cycle_duration - elapsed_time
                         
                         # 최소 60초는 상세 페이지에서 보내도록 보장
                         if remaining_time < 60:
                             remaining_time = 60
                             self.log(f"⚠️ 남은 시간 부족, 최소 60초 보장")
                         
                         self.log(f"⏱️ 지금까지 {int(elapsed_time)}초 경과, 상세 페이지에서 {int(remaining_time)}초 체류 예정")
                         self.do_product_interaction(remaining_time, cycle_start_time)
                    else:
                        self.log("❌ 타겟 찾기 실패.")
                    
                    self.log(f"{current_work.upper()} 작업 종료. 브라우저 닫음.")
                    try: self.driver.delete_all_cookies(); self.driver.quit()
                    except: pass
                    self.driver = None
                    
                    if len(work_plan) > 1 and current_work == work_plan[0]:
                         short_wait = random.randint(10, 30)
                         self.log(f"다음 작업({work_plan[1]}) 전 {short_wait}초 대기...")
                         time.sleep(short_wait)

                # [제거됨] 사이클 종료 후 추가 대기는 이제 불필요
                # 모든 시간이 이미 예열 + 검색 + 상세 인터랙션에서 소진됨
                self.log(f"✅ 사이클 완료. 다음 사이클 시작...")
            except Exception as e:
                self.log(f"Cycle Error: {e}")
                time.sleep(10)

    def update_timer_label(self, text):
        try:
            if hasattr(self.config_manager, 'app_ref') and self.config_manager.app_ref:
                self.config_manager.app_ref.lbl_timer.config(text=text)
        except: pass

    def do_product_interaction(self, remaining_time, cycle_start_time):
        """상세 페이지에서 사람처럼 행동"""
        self.log("상세 페이지 정독 시작...")
        interaction_start = time.time()
        
        # 1. 갤러리/썸네일 구경 (초반 시선 끌기)
        try:
            self.log("갤러리 이미지 탐색...")
            thumbs = self.driver.find_elements(By.CSS_SELECTOR, "div.mask_thumb_list, div.image_thumb_list, .product_images img, .image_thumb img")
            if thumbs:
                limit = min(len(thumbs), 5)
                for i in range(limit):
                    if not self.is_running: break
                    try:
                        self.mouse.smooth_move_to(thumbs[i])
                        time.sleep(random.uniform(0.5, 1.5))  # 마우스 이동 후 자연스러운 대기
                        thumbs[i].click()
                        time.sleep(random.uniform(1.5, 3.0))  # 이미지 감상 시간
                    except: pass
        except: pass
        
        # 2. 상세정보 펼쳐보기 (필수)
        try:
            time.sleep(random.uniform(1, 2))  # 페이지 로딩 후 자연스러운 탐색
            expand_btn = self.driver.find_element(By.XPATH, "//*[contains(text(), '펼쳐보기') or contains(text(), '상품정보 더보기')]")
            self.mouse.smooth_move_to(expand_btn)
            time.sleep(random.uniform(0.5, 1.5))  # 버튼 확인 후 클릭 전 대기
            expand_btn.click()
            self.log("상세정보 더보기 클릭 완료")
            time.sleep(random.uniform(2, 3))  # 상세정보 로딩 대기
        except: pass
        
        # 3. 옵션 선택 시뮬레이션 (구매 의도 강력 신호)
        try:
            self.log("옵션 선택 시뮬레이션...")
            opt_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '옵션') or contains(@class, 'option')] | //div[contains(@class, 'Option_option')]")
            self.mouse.smooth_move_to(opt_btn)
            time.sleep(random.uniform(0.5, 1.5))  # 옵션 버튼 확인 후 클릭 전 대기
            opt_btn.click()
            time.sleep(random.uniform(1.0, 2.0))  # 옵션 목록 로딩 대기
            
            opts = self.driver.find_elements(By.TAG_NAME, "li")
            if opts:
                target_opt = random.choice(opts[:5])
                self.mouse.smooth_move_to(target_opt)
                time.sleep(random.uniform(0.8, 1.5))  # 옵션 고민 시간
            
            ActionChains(self.driver).move_by_offset(50, 50).click().perform()
            time.sleep(random.uniform(1, 2))  # 옵션 닫기 후 대기
        except: pass
        
        # 4. 정독(Deep Read) 스크롤링 & 랜덤 액션
        # [수정] 전달받은 remaining_time 사용 (최소 60초 보장됨)
        end_time = time.time() + remaining_time
        last_log_time = time.time()
        
        while time.time() < end_time:
            if not self.is_running:
                self.log("⛔ 사용자가 중지 요청 - 상세 페이지 종료")
                break
            
            remain_time = end_time - time.time()
            if remain_time < 0: break
            
            # 10초마다 카운트다운 표시 (너무 자주 표시하지 않도록)
            current_time = time.time()
            if current_time - last_log_time >= 10:
                self.log(f"⏱️ 상세 페이지 체류 중... (남은: {int(remain_time)}초)")
                last_log_time = current_time
            
            actions = ["scroll_slow", "highlight_text", "review_read", "qna_read"]
            weights = [40, 20, 20, 20]
            
            if random.random() < 0.1:
                actions.append("wish_cart")
                weights.append(5)
            
            act = random.choices(actions, weights=weights, k=1)[0]
            
            try:
                if act == "scroll_slow":
                    for _ in range(random.randint(3, 6)):
                        self.driver.execute_script(f"window.scrollBy({{top: {random.randint(100, 300)}, behavior: 'smooth'}});")
                        time.sleep(random.uniform(1.0, 3.0))
                
                elif act == "highlight_text":
                    try:
                        desc = self.driver.find_element(By.CSS_SELECTOR, "div.se-main-container, .detail_detail_area")
                        self.mouse.smooth_move_to(desc)
                        ActionChains(self.driver).click_and_hold(desc).move_by_offset(random.randint(10, 50), random.randint(0, 10)).release().perform()
                        time.sleep(1)
                    except: pass
                
                elif act == "review_read":
                    btn = self.driver.find_element(By.XPATH, "//*[contains(text(), '리뷰') or contains(text(), '구매평')]")
                    self.mouse.smooth_move_to(btn)
                    btn.click()
                    time.sleep(random.uniform(3, 6))
                
                elif act == "qna_read":
                    try:
                        btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Q&A') or contains(text(), '문의')]")
                        self.mouse.smooth_move_to(btn)
                        btn.click()
                        time.sleep(2)
                        
                        qna_items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='question'], li[class*='question'], a[class*='product_qna']")
                        valid_qnas = [q for q in qna_items if q.is_displayed()]
                        
                        if valid_qnas:
                            target_q = random.choice(valid_qnas[:4])
                            self.mouse.smooth_move_to(target_q)
                            target_q.click()
                            self.log("다른 구매자의 Q&A를 읽는 중...")
                            time.sleep(random.uniform(3, 5))
                            target_q.click()
                            time.sleep(1)
                    except: pass
                
                elif act == "wish_cart":
                    btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '찜') or contains(text(), '장바구니')]")
                    if btns:
                        b = random.choice(btns)
                        self.mouse.smooth_move_to(b)
                        self.log("구매 시그널(찜/장바구니) 클릭 시도")
                        b.click()
                        time.sleep(2)
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            
            except: pass
            
            time.sleep(random.randint(2, 4))

class DelaySettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("딜레이 설정")
        self.config = config
        self.entries = {}
        row = 0
        keys = ["search_delay", "scroll_delay", "click_delay"]
        labels = ["검색 타이핑 간격", "스크롤 대기 시간", "클릭 후 대기 시간"]
        for k, label in zip(keys, labels):
            tk.Label(self, text=label).grid(row=row, column=0, padx=5, pady=5)
            f = tk.Frame(self); f.grid(row=row, column=1)
            e_min = tk.Entry(f, width=8); e_min.insert(0, str(config['delays'].get(f"{k}_min", 1000))); e_min.pack(side="left")
            tk.Label(f, text="~").pack(side="left")
            e_max = tk.Entry(f, width=8); e_max.insert(0, str(config['delays'].get(f"{k}_max", 2000))); e_max.pack(side="left")
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
            messagebox.showinfo("저장", "설정이 저장되었습니다."); self.destroy()
        except ValueError: messagebox.showerror("오류", "숫자만 입력하세요.")

# [추가] 서버 API 설정
API_BASE_URL = "http://localhost:8000"

class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PartnerChain Login")
        self.geometry("350x250")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.token = None # 로그인 성공 시 저장될 토큰
        self.user_info = None
        
        # Styles
        style = ttk.Style()
        style.configure("Login.TLabel", font=("Malgun Gothic", 10))
        style.configure("Login.TButton", font=("Malgun Gothic", 10, "bold"))
        
        # UI Elements
        frame = ttk.Frame(self, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="PartnerChain Bot Login", font=("Malgun Gothic", 14, "bold"), foreground="#2c3e50").pack(pady=(0, 20))
        
        ttk.Label(frame, text="아이디 (Username):", style="Login.TLabel").pack(anchor="w")
        self.entry_user = ttk.Entry(frame, width=30)
        self.entry_user.pack(pady=(0, 10), fill=tk.X)
        self.entry_user.focus_set()
        
        ttk.Label(frame, text="비밀번호 (Password):", style="Login.TLabel").pack(anchor="w")
        self.entry_pw = ttk.Entry(frame, show="*", width=30)
        self.entry_pw.pack(pady=(0, 15), fill=tk.X)
        self.entry_pw.bind("<Return>", lambda e: self.do_login())
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="로그인 (Login)", style="Login.TButton", command=self.do_login).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(btn_frame, text="종료 (Exit)", command=self.do_exit).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))
        
        self.protocol("WM_DELETE_WINDOW", self.do_exit)
        self.parent = parent

    def do_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pw.get().strip()
        
        if not username or not password:
            messagebox.showwarning("입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return

        try:
            # 1. Get Token
            resp = requests.post(f"{API_BASE_URL}/token", data={"username": username, "password": password})
            
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                
                # 2. Get User Info (License check logic can be added here)
                headers = {"Authorization": f"Bearer {self.token}"}
                user_resp = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
                
                if user_resp.status_code == 200:
                    self.user_info = user_resp.json()
                    # Check License Validity (Optional: Check if user has active license)
                    # For now, just allow login if authenticated
                    
                    messagebox.showinfo("로그인 성공", f"환영합니다, {username}님!")
                    self.destroy() # Close login dialog
                else:
                     messagebox.showerror("오류", "사용자 정보를 불러올 수 없습니다.")
            elif resp.status_code == 401:
                messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 잘못되었습니다.")
            else:
                messagebox.showerror("서버 오류", f"로그인 중 문제가 발생했습니다. (Code: {resp.status_code})")
                
        except Exception as e:
            messagebox.showerror("연결 오류", f"서버에 접속할 수 없습니다.\n{e}")

    def do_exit(self):
        self.parent.destroy() # Close main window too
        self.destroy()

class BotApp:
    def __init__(self, root, expiration_date=None):
        self.root = root
        title = "네이버 쇼핑/블로그 멀티 봇 v4.3 (Final Polish)"
        self.root.title(title)
        self.root.geometry("720x980") 
        
        if LICENSE_DATA:
            days = LICENSE_DATA.get('days_remaining', 0)
            memo = LICENSE_DATA.get('memo') or "Unknown"
            exp_txt = f"남은 기간: {days}일"
            f_lic = tk.Frame(self.root, bg="#e8f5e9", pady=5)
            f_lic.pack(fill="x")
            tk.Label(f_lic, text=f"🏢 회사명: {memo}", font=("Arial", 10, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(side="left", padx=20)
            tk.Label(f_lic, text=f"⏳ {exp_txt}", font=("Arial", 10), bg="#e8f5e9", fg="#2e7d32").pack(side="right", padx=20)

        self.config = ConfigManager.load()
        if "targets" in self.config and self.config["targets"]:
             if not self.config.get("targets_shopping"): self.config["targets_shopping"] = self.config["targets"]
             del self.config["targets"]
        
        self.logic = BotLogic(self.log, self.config, self.on_success_ui)
        self.logic.config_manager = type('obj', (object,), {'app_ref': self}) 
        self.create_ui()

    def create_ui(self):
        f_top = tk.LabelFrame(self.root, text="공통 설정")
        f_top.pack(fill="x", padx=10, pady=5)
        
        tk.Label(f_top, text="Min(분):").pack(side="left")
        self.e_min = tk.Entry(f_top, width=3); self.e_min.insert(0, self.config.get("min_time_min", 3)); self.e_min.pack(side="left", padx=2)
        tk.Label(f_top, text="Max(분):").pack(side="left")
        self.e_max = tk.Entry(f_top, width=3); self.e_max.insert(0, self.config.get("max_time_min", 5)); self.e_max.pack(side="left", padx=2)
        
        tk.Label(f_top, text="| 모드:").pack(side="left", padx=5)
        self.combo_mode = ttk.Combobox(f_top, values=["PC", "Mobile", "Random"], width=7, state="readonly")
        self.combo_mode.set(self.config.get("mode", "PC")); self.combo_mode.pack(side="left")
        
        self.var_smart = tk.BooleanVar(value=self.config.get("smart_schedule", True))
        self.var_ads = tk.BooleanVar(value=self.config.get("include_ads", True))
        
        tk.Checkbutton(f_top, text="스마트 스케줄", variable=self.var_smart).pack(side="left", padx=5)
        # 삭제되었던 '광고 포함' 체크박스 복구
        tk.Checkbutton(f_top, text="광고 포함", variable=self.var_ads).pack(side="left", padx=5)
        
        tk.Button(f_top, text="설정", command=self.open_settings).pack(side="right", padx=5)
        
        # [NEW] 혼합 모드 체크박스 (별도 행 - 공통 설정 아래)
        f_mid = tk.Frame(self.root)
        f_mid.pack(fill="x", padx=10, pady=0)
        self.var_mixed = tk.BooleanVar(value=self.config.get("mixed_mode", True))
        chk_mix = tk.Checkbutton(f_mid, text="✨ 네이버 쇼핑 + 블로그 바이럴 (통합 사이클 실행)", 
                               variable=self.var_mixed, font=("Arial", 10, "bold"), fg="#3f51b5")
        chk_mix.pack(pady=5)
        
        self.lbl_timer = tk.Label(self.root, text="대기 중...", font=("Arial", 18, "bold"), fg="#FF5722")
        self.lbl_timer.pack(pady=10)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_shopping = tk.Frame(self.notebook)
        self.notebook.add(self.tab_shopping, text="   🛒 네이버 쇼핑   ")
        self.setup_tab_content(self.tab_shopping, "shopping")
        
        self.tab_blog = tk.Frame(self.notebook)
        self.notebook.add(self.tab_blog, text="   📝 블로그/바이럴   ")
        self.setup_tab_content(self.tab_blog, "blog")

        f_bottom = tk.Frame(self.root)
        f_bottom.pack(fill="both", expand=True, padx=10, pady=5)
        self.btn_start = tk.Button(f_bottom, text="START (실행)", command=self.toggle_start, bg="#4CAF50", fg="white", font=("Bold", 14), height=2)
        self.btn_start.pack(fill="x", pady=5)
        
        self.log_area = scrolledtext.ScrolledText(f_bottom, height=8)
        self.log_area.pack(fill="both", expand=True)

    def setup_tab_content(self, parent, mode):
        f_in = tk.Frame(parent); f_in.pack(fill="x", pady=5)
        tk.Label(f_in, text="1차 키워드:").grid(row=0, column=0)
        e_k1 = tk.Entry(f_in, width=12); e_k1.grid(row=0, column=1)
        tk.Label(f_in, text="2차:").grid(row=0, column=2)
        e_k2 = tk.Entry(f_in, width=12); e_k2.grid(row=0, column=3)
        lbl_id = "상품ID:" if mode == "shopping" else "식별자:"
        tk.Label(f_in, text=lbl_id).grid(row=0, column=4)
        e_id = tk.Entry(f_in, width=10); e_id.grid(row=0, column=5)
        # [수정] 판매링크 -> 타겟 링크 (블로그 모드에서만 표시)
        if mode == "blog":
            tk.Label(f_in, text="타겟 링크:").grid(row=0, column=6)
            e_plink = tk.Entry(f_in, width=15); e_plink.grid(row=0, column=7)
            btn_f = tk.Frame(f_in); btn_f.grid(row=0, column=8, columnspan=3, padx=5)
        else:
            e_plink = None
            btn_f = tk.Frame(f_in); btn_f.grid(row=0, column=6, columnspan=3, padx=5)
        
        cols = ("k1", "k2", "id", "plink", "cnt") if mode == "blog" else ("k1", "k2", "id", "cnt")
        tree = ttk.Treeview(parent, columns=cols, show="headings")
        tree.heading("k1", text="1차 키워드"); tree.column("k1", width=120)
        tree.heading("k2", text="2차 키워드"); tree.column("k2", width=120)
        tree.heading("id", text="ID/식별자"); tree.column("id", width=100)
        if mode == "blog":
            tree.heading("plink", text="판매링크"); tree.column("plink", width=150)
        tree.heading("cnt", text="성공"); tree.column("cnt", width=50, anchor="center")
        tree.pack(fill="both", expand=True)
        
        if mode == "blog":
            tk.Button(btn_f, text="추가", command=lambda: self.add_item(mode, e_k1, e_k2, e_id, tree, e_plink)).pack(side="left")
            tk.Button(btn_f, text="수정", command=lambda: self.update_item(mode, e_k1, e_k2, e_id, tree, e_plink)).pack(side="left")
            tk.Button(btn_f, text="삭제", command=lambda: self.del_item(mode, tree)).pack(side="left")
            tree.bind("<<TreeviewSelect>>", lambda event: self.on_tree_select(event, e_k1, e_k2, e_id, tree, e_plink))
        else:
            tk.Button(btn_f, text="추가", command=lambda: self.add_item(mode, e_k1, e_k2, e_id, tree)).pack(side="left")
            tk.Button(btn_f, text="수정", command=lambda: self.update_item(mode, e_k1, e_k2, e_id, tree)).pack(side="left")
            tk.Button(btn_f, text="삭제", command=lambda: self.del_item(mode, tree)).pack(side="left")
            tree.bind("<<TreeviewSelect>>", lambda event: self.on_tree_select(event, e_k1, e_k2, e_id, tree))
        
        targets = self.config.get(f"targets_{mode}", [])
        for t in targets:
            if mode == "blog":
                tree.insert("", "end", values=(t['keyword'], t.get("keyword_2", ""), t['id'], t.get("product_link", ""), t.get("success_count", 0)))
            else:
                tree.insert("", "end", values=(t['keyword'], t.get("keyword_2", ""), t['id'], t.get("success_count", 0)))
        setattr(self, f"tree_{mode}", tree)

    def on_tree_select(self, event, e_k1, e_k2, e_id, tree, e_plink=None):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])['values']
        e_k1.delete(0, tk.END); e_k1.insert(0, vals[0])
        e_k2.delete(0, tk.END); 
        if str(vals[1]) not in ["None", ""]: e_k2.insert(0, vals[1])
        e_id.delete(0, tk.END); e_id.insert(0, vals[2])
        if e_plink:
            e_plink.delete(0, tk.END)
            if len(vals) > 3 and str(vals[3]) not in ["None", ""]:
                e_plink.insert(0, vals[3])

    def add_item(self, mode, e_k1, e_k2, e_id, tree, e_plink=None):
        k1, k2, i = e_k1.get(), e_k2.get(), e_id.get()
        plink = e_plink.get() if e_plink else ""
        if k1 and i:
            if mode == "blog":
                tree.insert("", "end", values=(k1, k2, i, plink, 0))
            else:
                tree.insert("", "end", values=(k1, k2, i, 0))
            self.save_current_state()
            e_k1.delete(0, tk.END); e_k2.delete(0, tk.END); e_id.delete(0, tk.END)
            if e_plink: e_plink.delete(0, tk.END)

    def update_item(self, mode, e_k1, e_k2, e_id, tree, e_plink=None):
        sel = tree.selection()
        if not sel: return
        k1, k2, i = e_k1.get(), e_k2.get(), e_id.get()
        plink = e_plink.get() if e_plink else ""
        if k1 and i:
            old = tree.item(sel[0])['values']
            if mode == "blog":
                tree.item(sel[0], values=(k1, k2, i, plink, old[4]))
            else:
                tree.item(sel[0], values=(k1, k2, i, old[3]))
            self.save_current_state()
            e_k1.delete(0, tk.END); e_k2.delete(0, tk.END); e_id.delete(0, tk.END)
            if e_plink: e_plink.delete(0, tk.END)

    def del_item(self, mode, tree):
        for s in tree.selection(): tree.delete(s)
        self.save_current_state()

    def open_settings(self):
        DelaySettingsDialog(self.root, self.config)

    def save_current_state(self):
        self.config["min_time_min"] = int(self.e_min.get())
        self.config["max_time_min"] = int(self.e_max.get())
        self.config["mode"] = self.combo_mode.get()
        self.config["smart_schedule"] = self.var_smart.get()
        self.config["include_ads"] = self.var_ads.get()
        self.config["mixed_mode"] = self.var_mixed.get() 
        for mode in ["shopping", "blog"]:
            tree = getattr(self, f"tree_{mode}")
            lst = []
            for item in tree.get_children():
                vals = tree.item(item)['values']
                if mode == "blog":
                    lst.append({"keyword": str(vals[0]), "keyword_2": str(vals[1]), "id": str(vals[2]), "product_link": str(vals[3]), "success_count": int(vals[4])})
                else:
                    lst.append({"keyword": str(vals[0]), "keyword_2": str(vals[1]), "id": str(vals[2]), "success_count": int(vals[3])})
            self.config[f"targets_{mode}"] = lst
        ConfigManager.save(self.config)

    def toggle_start(self):
        if self.logic.is_running:
            self.logic.is_running = False
            self.log("중단 요청...")
            self.btn_start.config(text="START (실행)", bg="#4CAF50")
        else:
            self.save_current_state()
            current_tab_index = self.notebook.index("current")
            mode = "shopping" if current_tab_index == 0 else "blog"
            self.config["work_type"] = mode 
            if self.config.get("mixed_mode"):
                if not self.config.get("targets_shopping") or not self.config.get("targets_blog"):
                     messagebox.showwarning("주의", "혼합 모드를 실행하려면 쇼핑과 블로그 타겟이 모두 최소 1개 이상 있어야 합니다.")
                     return
            else:
                if not self.config.get(f"targets_{mode}"):
                    messagebox.showerror("Err", f"{mode} 모드의 타겟이 없습니다.")
                    return
            self.log(f"=== 봇 시작 ===")
            self.logic.is_running = True
            self.btn_start.config(text="STOP (작동 중...)", bg="#f44336")
            min_t = int(self.e_min.get())
            max_t = int(self.e_max.get())
            run_mode = self.combo_mode.get()
            threading.Thread(target=self.logic.run_cycle_loop, args=(min_t, max_t, run_mode), daemon=True).start()

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def on_success_ui(self, target_id):
        self.root.after(0, lambda: self._update_count(target_id))

    def _update_count(self, target_id):
        for mode in ["shopping", "blog"]:
            tree = getattr(self, f"tree_{mode}")
            for item in tree.get_children():
                vals = tree.item(item)['values']
                if str(vals[2]) == str(target_id):
                    new_cnt = int(vals[3]) + 1
                    tree.item(item, values=(vals[0], vals[1], vals[2], new_cnt))
                    self.save_current_state()
                    return 

def main():
    try:
        # 1. 라이선스 체크 (시리얼 키 & MAC 주소 검증)
        try:
            from license_check import check_license
            # check_license()는 유효하지 않으면 내부에서 UI로 키 입력을 받거나 종료함
            # 유효하면 데이터를 반환
            lic_data = check_license()
            
            if not lic_data or not lic_data.get("valid"):
                # check_license에서 이미 처리했겠지만 안전장치
                sys.exit(0)
                
            # 전역 변수에 라이선스 정보 설정 (BotApp에서 사용)
            global LICENSE_DATA
            LICENSE_DATA = lic_data
            
        except ImportError:
            # 라이선스 모듈이 없는 경우 (개발 환경 등) - 경고 후 진행 여부 결정
            # 상용 배포판에서는 이 경로가 없어야 함
            messagebox.showwarning("경고", "라이선스 모듈(license_check.py)을 찾을 수 없습니다.\n데모 모드로 실행됩니다.")
            LICENSE_DATA = {"valid": True, "memo": "DEMO MODE", "days_remaining": 0}

        # 2. 봇 실행
        root = tk.Tk()
        # BotApp 초기화 - 라이선스 만료일 전달
        app = BotApp(root, expiration_date=LICENSE_DATA.get("expiration_date"))
        root.mainloop()

    except Exception as e:
        print(f"Main Error: {e}")
        # traceback.print_exc()
        time.sleep(5)

if __name__ == "__main__":
    main()
