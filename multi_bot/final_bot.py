import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
from webdriver_manager.chrome import ChromeDriverManager
from random_data import GENERIC_KEYWORDS

# 상수 - 경로 설정 (Portable)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUGNER_PORT = 9222
DEBUGGER_ADDRESS = f"127.0.0.1:{DEBUGNER_PORT}"
CONFIG_FILE = os.path.join(BASE_DIR, 'bot_config.json')
LICENSE_FILE = os.path.join(BASE_DIR, 'license.dat')

class ConfigManager:
    @staticmethod
    def load():
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "min_time_min": 2,
                "max_time_min": 3,
                "mode": "Random",
                "smart_schedule": True,
                "include_ads": False,
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

# 시각화 스크립트
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
        try: self.driver.execute_script(VISUAL_JS)
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
                self.driver.execute_script(f"window.moveBotCursor({x}, {y}, {'true' if is_mobile else 'false'});")
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
        self.wait = None

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
            else:
                self.driver.set_window_size(1920, 1080)
                self.driver.maximize_window()
            
            self.mouse = NaturalMouse(self.driver)
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            self.log(f"드라이버 시작 실패: {e}")
            return False

    def human_typing(self, element, text):
        try:
            element.click()
            time.sleep(0.5)
            element.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.1)
            element.send_keys(Keys.BACK_SPACE)
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
        if 0 <= hour < 7: return 4.0
        if 7 <= hour < 10: return 1.5
        if 10 <= hour < 19: return 1.0
        if 19 <= hour < 24: return 0.8
        return 1.0

    def calculate_cycle_time(self, min_t, max_t):
        base = random.randint(min_t * 60, max_t * 60)
        mult = self.get_schedule_multiplier()
        final = int(base * mult)
        self.log(f"스마트 스케줄 적용: {mult}배 (다음 사이클 대기: {final}초)")
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
            # 1. 숫자 클릭
            try:
                next_btn = self.driver.find_element(By.XPATH, f"//a[text()='{page_num}']")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass
            # 2. '다음' 버튼
            try:
                next_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '다음')]")
                self.mouse.smooth_move_to(next_btn)
                next_btn.click()
                return True
            except: pass
            return False
        except: return False

    # --- 분리된 로직 시작 ---

    def process_shopping(self, target):
        t_kw1 = target['keyword']
        t_kw2 = target.get('keyword_2', '')
        t_id = target['id']
        max_pages = self.config.get('max_pages', 3)
        include_ads = self.config.get('include_ads', True)

        def search_logic(input_kw):
            self.log(f"[쇼핑] 검색: {input_kw}")
            self.driver.get("https://www.naver.com")
            time.sleep(2)
            try:
                if self.current_mode == "Mobile":
                    try: self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click(); time.sleep(1)
                    except: pass
                s_box = self.wait.until(EC.element_to_be_clickable((By.ID, "query")))
                self.human_typing(s_box, input_kw)
                s_box.send_keys(Keys.RETURN)
                time.sleep(2)
            except:
                self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")
                time.sleep(2)
            
            self.check_and_switch_tab()
            
            # 더보기 탐색
            found_more = False
            try:
                for _ in range(3):
                    self.human_scroll(max_scrolls=1)
                    btns = self.driver.find_elements(By.XPATH, "//*[contains(text(), '가격비교 더보기') or contains(text(), '쇼핑 더보기')]")
                    for b in btns:
                        if b.is_displayed():
                            self.mouse.smooth_move_to(b); b.click(); found_more = True; break
                    if found_more: break
            except: pass
            
            if not found_more:
                self.driver.get(f"https://search.shopping.naver.com/search/all?query={input_kw}")
            
            self.check_and_switch_tab()
            time.sleep(2)

            for p in range(1, max_pages + 1):
                self.log(f"쇼핑 {p}페이지 탐색 중...")
                self.human_scroll(max_scrolls=3)
                el = self.find_target_on_page(t_id, include_ads)
                if el:
                    self.log("타겟 발견! 클릭.")
                    self.mouse.smooth_move_to(el)
                    try: el.click()
                    except: self.driver.execute_script("arguments[0].click()", el)
                    time.sleep(3)
                    self.check_and_switch_tab()
                    return True
                if p < max_pages:
                    if not self.go_to_next_page(p + 1): break
                    time.sleep(3)
            return False

        success = search_logic(t_kw1)
        if not success and t_kw2:
            self.log("1차 실패. 2차 시도...")
            success = search_logic(t_kw2)
        return success

    def process_blog(self, target):
        t_kw1 = target['keyword']
        t_kw2 = target.get('keyword_2', '')
        t_id = target['id']
        max_pages = self.config.get('max_pages', 3)

        def search_blog(kw, target_check, is_retry):
            self.driver.get("https://www.naver.com")
            time.sleep(2)
            
            # Fake Search
            for _ in range(random.randint(1, 2)):
                if not self.is_running: return False
                try:
                    if self.current_mode == "Mobile":
                        try: self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click(); time.sleep(1)
                        except: pass
                    s_box = self.wait.until(EC.element_to_be_clickable((By.ID, "query")))
                    self.human_typing(s_box, random.choice(GENERIC_KEYWORDS))
                    s_box.send_keys(Keys.RETURN)
                    time.sleep(2)
                    self.driver.get("https://www.naver.com")
                    time.sleep(2)
                except: pass

            self.log(f"[블로그] 검색: {kw}")
            try:
                if self.current_mode == "Mobile":
                    try: self.driver.find_element(By.ID, "MM_SEARCH_FAKE").click(); time.sleep(1)
                    except: pass
                s_box = self.wait.until(EC.element_to_be_clickable((By.ID, "query")))
                self.human_typing(s_box, kw)
                s_box.send_keys(Keys.RETURN)
                time.sleep(2)
            except: return False

            self.check_and_switch_tab()
            
            # 더보기/탭 탐색
            found_more = False
            for _ in range(5):
                self.human_scroll(max_scrolls=1)
                xpaths = ["//*[contains(text(), 'VIEW 더보기')]", "//*[contains(text(), '블로그 더보기')]", "//*[contains(text(), '검색결과 더보기')]"]
                for xp in xpaths:
                    try:
                        btns = self.driver.find_elements(By.XPATH, xp)
                        for b in btns:
                            if b.is_displayed():
                                self.mouse.smooth_move_to(b); b.click(); found_more = True; break
                    except: pass
                    if found_more: break
                if found_more: break
            
            if not found_more:
                try: 
                    self.driver.find_element(By.XPATH, "//*[text()='VIEW' or text()='블로그']").click()
                    time.sleep(2)
                except: pass

            found_blog = False
            max_tries = 10 if not is_retry else max_pages * 5
            
            for i in range(max_tries):
                if not self.is_running: break
                titles = self.driver.find_elements(By.CSS_SELECTOR, "a.api_txt_lines, a.total_tit, .view_tit, a.title_link")
                for t in titles:
                    try:
                        if target_check and target_check in t.text:
                            self.log(f"블로그 발견: {t.text}")
                            self.human_scroll(max_scrolls=1)
                            self.mouse.smooth_move_to(t); t.click(); found_blog = True; break
                    except: pass
                if found_blog: break
                
                # Check text body fallback
                if not found_blog and target_check:
                    try:
                        cands = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{target_check}')]")
                        for c in cands:
                            if c.is_displayed():
                                # find parent a
                                p = c
                                for _ in range(5):
                                    if p.tag_name == 'a': 
                                        self.mouse.smooth_move_to(p); p.click(); found_blog = True; break
                                    try: p = p.find_element(By.XPATH, ".."); 
                                    except: break
                            if found_blog: break
                    except: pass
                if found_blog: break
                
                self.human_scroll(max_scrolls=1)
            
            if not found_blog: 
                self.log("블로그 글을 찾지 못함")
                return False
                
            self.check_and_switch_tab()
            time.sleep(3)
            
            # 정독 및 링크 찾기
            self.log("블로그 정독 및 링크 탐색...")
            is_iframe = False
            try: self.driver.switch_to.frame("mainFrame"); is_iframe = True
            except: pass
            
            found_link = None
            start_read = time.time()
            while time.time() - start_read < 90:
                if not self.is_running: break
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for l in links:
                        try:
                            h = l.get_attribute("href") or ""
                            t = l.text or ""
                            inner = l.get_attribute("innerText") or ""
                            if (t_id in h) or (t_id in t) or (t_id in inner):
                                self.log(f"링크 발견 ({t_id})")
                                found_link = l
                                break
                        except: pass
                    if found_link: break
                except: pass
                self.human_scroll(max_scrolls=1)
                time.sleep(1)
            
            if found_link:
                self.log("링크 클릭")
                self.mouse.smooth_move_to(found_link)
                found_link.click()
                if is_iframe: self.driver.switch_to.default_content()
                time.sleep(3)
                self.check_and_switch_tab()
                return True
            else:
                self.log("링크 미발견")
                if is_iframe: self.driver.switch_to.default_content()
                return False

        success = search_blog(t_kw1, t_kw2, False)
        if not success and t_kw2:
            self.log("1차 실패, Fallback 재시도...")
            success = search_blog(t_kw2, t_kw2, True)
        return success

    def run_wrapper(self, loop_func, *args):
        # Wrapper to start timer thread
        threading.Thread(target=self._timer_loop, daemon=True).start()
        loop_func(*args)

    def run_cycle_loop(self, targets, min_t, max_t, mode_setting, work_type="shopping"):
        while self.is_running:
            try:
                cycle_duration = self.calculate_cycle_time(min_t, max_t)
                start_time = time.time()
                self.cycle_start_time = start_time
                self.cycle_total_duration = cycle_duration
                
                self.log(f"=== {work_type.upper()} 사이클 시작 ({cycle_duration}초) ===")
                
                if not self.setup_driver(mode_setting):
                    time.sleep(5); continue

                if not targets:
                    self.log("타겟 없음. 대기..."); time.sleep(10); continue
                
                target = random.choice(targets)
                success = False
                if work_type == "shopping":
                    success = self.process_shopping(target)
                else:
                    success = self.process_blog(target)
                
                if success:
                    self.log("타겟 진입 성공. 상세 인터랙션 진행.")
                    if self.on_success: self.on_success(target['id'])
                    self.do_product_interaction(cycle_duration, start_time)
                else:
                    self.log("타겟 찾기 실패.")
                
                try: self.driver.delete_all_cookies(); self.driver.quit()
                except: pass
                self.driver = None
                self.update_timer_label("대기 중...")
                
            except Exception as e:
                self.log(f"Error: {e}")
                try: self.driver.quit(); self.driver = None
                except: pass

    def run_integrated_loop(self, targets_shop, targets_blog, min_t, max_t, mode_setting):
        while self.is_running:
            # 1. Shopping Cycle
            if targets_shop:
                try:
                    cycle_duration = self.calculate_cycle_time(min_t, max_t)
                    start_time = time.time()
                    self.cycle_start_time = start_time
                    self.cycle_total_duration = cycle_duration
                    
                    self.log(f"=== [통합] 쇼핑 사이클 시작 ({cycle_duration}초) ===")
                    if self.setup_driver(mode_setting):
                        target = random.choice(targets_shop)
                        if self.process_shopping(target):
                            self.log("쇼핑 성공. 인터랙션...")
                            if self.on_success: self.on_success(target['id'])
                            self.do_product_interaction(cycle_duration, start_time)
                        else: self.log("쇼핑 타겟 실패")
                        try: self.driver.delete_all_cookies(); self.driver.quit()
                        except: pass
                        self.driver = None
                except Exception as e: self.log(f"Shop Error: {e}")
                self.update_timer_label("대기 중...")
            
            if not self.is_running: break
            time.sleep(2)
            
            # 2. Blog Cycle
            if targets_blog:
                try:
                    cycle_duration = self.calculate_cycle_time(min_t, max_t) # Calculate again for variety
                    start_time = time.time()
                    self.cycle_start_time = start_time
                    self.cycle_total_duration = cycle_duration

                    self.log(f"=== [통합] 블로그 사이클 시작 ({cycle_duration}초) ===")
                    if self.setup_driver(mode_setting):
                        target = random.choice(targets_blog)
                        if self.process_blog(target):
                            self.log("블로그 성공. 인터랙션...")
                            if self.on_success: self.on_success(target['id'])
                            self.do_product_interaction(cycle_duration, start_time)
                        else: self.log("블로그 타겟 실패")
                        try: self.driver.delete_all_cookies(); self.driver.quit()
                        except: pass
                        self.driver = None
                except Exception as e: self.log(f"Blog Error: {e}")
                self.update_timer_label("대기 중...")

            if not targets_shop and not targets_blog:
                self.log("타겟이 없습니다."); time.sleep(10)

    def do_product_interaction(self, cycle_duration, start_time):
        self.log("상세 페이지 정독 중...")
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(400, 800)});")
                time.sleep(random.uniform(1.0, 3.0))
                elapsed = time.time() - start_time
                if elapsed > cycle_duration: break
                new = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
                if new >= last_height - 100: break
            
            # Action check
            candidates = ["리뷰 보기", "구매평 보기", "Q&A", "상품문의"]
            for c in candidates:
                btns = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{c}')]")
                if btns:
                    for b in btns:
                        if b.is_displayed():
                            try: self.mouse.smooth_move_to(b); b.click(); time.sleep(2); break
                            except: pass
                    break
        except: pass
        
        self.log("잔여 시간 Active Idle...")
        while True:
             elapsed = time.time() - start_time
             if elapsed > cycle_duration: break
             if not self.is_running: break
             try:
                 act = random.choice(["up", "down", "move"])
                 if act == "up": self.driver.execute_script("window.scrollBy(0, -200)")
                 elif act == "down": self.driver.execute_script("window.scrollBy(0, 200)")
                 else: ActionChains(self.driver).move_by_offset(random.randint(-10,10), random.randint(-10,10)).perform()
             except: pass
             time.sleep(3)

    def update_timer_label(self, text):
        try:
            if hasattr(self, 'config_manager') and hasattr(self.config_manager, 'app_ref'):
                self.config_manager.app_ref.lbl_timer.config(text=text)
        except: pass

class DelaySettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("딜레이 설정")
        self.config = config
        self.entries = {}
        row = 0
        for k, l in [("search_delay", "검색"), ("scroll_delay", "스크롤"), ("click_delay", "클릭")]:
            tk.Label(self, text=l).grid(row=row, column=0)
            f = tk.Frame(self); f.grid(row=row, column=1)
            e1 = tk.Entry(f, width=5); e1.insert(0, config['delays'].get(f"{k}_min", 1000)); e1.pack(side="left")
            tk.Label(f, text="~").pack(side="left")
            e2 = tk.Entry(f, width=5); e2.insert(0, config['delays'].get(f"{k}_max", 2000)); e2.pack(side="left")
            self.entries[k] = (e1, e2)
            row += 1
        tk.Button(self, text="저장", command=self.save).grid(row=row, columnspan=2)

    def save(self):
        try:
            for k, (e1, e2) in self.entries.items():
                self.config['delays'][f"{k}_min"] = int(e1.get())
                self.config['delays'][f"{k}_max"] = int(e2.get())
            ConfigManager.save(self.config)
            self.destroy()
        except: pass

class BotApp:
    def __init__(self, root, expiration_date=None):
        self.root = root
        
        # UI v4.2 Update
        self.root.title("네이버 쇼핑/블로그 멀티 봇 v4.2 (Secure Commercial)")
        self.root.geometry("700x980")
        
        # Read License for Company Name
        company_name = "Demo User"
        if os.path.exists(LICENSE_FILE):
             with open(LICENSE_FILE, "r") as f:
                 company_name = f.read().strip()
        
        # Company Name Header
        tk.Label(self.root, text=f"  ♠ 회사명: {company_name}", font=("Arial", 10, "bold"), fg="green", anchor="w").pack(fill="x", pady=5)

        if expiration_date:
            tk.Label(self.root, text=f"⌛ 남은 기간: {expiration_date}", fg="green", anchor="e").pack(fill="x", padx=10)
        
        self.config = ConfigManager.load()
        if "targets" in self.config:
            if not self.config.get("targets_shopping"): self.config["targets_shopping"] = self.config["targets"]
            del self.config["targets"]

        self.logic = BotLogic(self.log, self.config, self.on_success_ui)
        self.logic.config_manager = type('obj', (object,), {'app_ref': self}) 
        self.create_ui()

    def create_ui(self):
        f_top = tk.LabelFrame(self.root, text="공통 설정")
        f_top.pack(fill="x", padx=10, pady=5)
        
        tk.Label(f_top, text="Min(분):").pack(side="left")
        self.e_min = tk.Entry(f_top, width=3); self.e_min.insert(0, self.config.get("min_time_min", 3)); self.e_min.pack(side="left")
        tk.Label(f_top, text="Max(분):").pack(side="left")
        self.e_max = tk.Entry(f_top, width=3); self.e_max.insert(0, self.config.get("max_time_min", 5)); self.e_max.pack(side="left")
        
        tk.Label(f_top, text="| 모드:").pack(side="left")
        self.combo = ttk.Combobox(f_top, values=["PC", "Mobile", "Random"], width=7, state="readonly")
        self.combo.set(self.config.get("mode", "PC"))
        self.combo.pack(side="left")
        
        self.var_smart = tk.BooleanVar(value=self.config.get("smart_schedule", True))
        self.var_ads = tk.BooleanVar(value=self.config.get("include_ads", True))
        tk.Checkbutton(f_top, text="스마트 스케줄", variable=self.var_smart).pack(side="left")
        tk.Checkbutton(f_top, text="광고 포함", variable=self.var_ads).pack(side="left")
        
        tk.Button(f_top, text="설정", command=lambda: DelaySettingsDialog(self.root, self.config)).pack(side="right")
        
        # Integrated Mode Checkbox
        self.var_integrated = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="✨ 네이버 쇼핑 + 블로그 바이럴 (통합 사이클 실행)", variable=self.var_integrated, font=("Arial", 11, "bold"), fg="#3F51B5").pack(pady=10)
        
        self.lbl_timer = tk.Label(self.root, text="대기 중...", font=("Arial", 16, "bold"), fg="#FF5722")
        self.lbl_timer.pack(pady=5)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10)
        
        self.tab_s = tk.Frame(self.notebook); self.notebook.add(self.tab_s, text=" 🛒 네이버 쇼핑 ")
        self.setup_tab(self.tab_s, "shopping")
        
        self.tab_b = tk.Frame(self.notebook); self.notebook.add(self.tab_b, text=" 📝 블로그/바이럴 ")
        self.setup_tab(self.tab_b, "blog")
        
        self.btn_start = tk.Button(self.root, text="START / STOP", command=self.toggle, bg="#4CAF50", fg="white", font=("Bold", 12))
        self.btn_start.pack(fill="x", padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self.root, height=10); self.log_area.pack(fill="both", padx=10, pady=5)

    def setup_tab(self, parent, mode):
        f = tk.Frame(parent); f.pack(fill="x")
        tk.Label(f, text="1차 키워드:").pack(side="left")
        k1 = tk.Entry(f, width=10); k1.pack(side="left")
        tk.Label(f, text="2차:").pack(side="left")
        k2 = tk.Entry(f, width=10); k2.pack(side="left")
        tk.Label(f, text="식별자:").pack(side="left")
        id_ = tk.Entry(f, width=10); id_.pack(side="left")
        
        tree = ttk.Treeview(parent, columns=("k1","k2","id","cnt"), show="headings", height=5)
        tree.heading("k1", text="1차 키워드"); tree.column("k1", width=120)
        tree.heading("k2", text="2차 키워드"); tree.column("k2", width=120)
        tree.heading("id", text="ID/식별자"); tree.column("id", width=120)
        tree.heading("cnt", text="성공"); tree.column("cnt", width=50)
        tree.pack(fill="both", expand=True)

        setattr(self, f"tree_{mode}", tree)
        
        # Load
        for t in self.config.get(f"targets_{mode}", []):
            tree.insert("", "end", values=(t['keyword'], t.get('keyword_2',''), t['id'], t.get('success_count', 0)))

        # Buttons
        f_btn = tk.Frame(f); f_btn.pack(side="right")
        tk.Button(f_btn, text="추가", command=lambda: self.add(mode, k1, k2, id_)).pack(side="left")
        tk.Button(f_btn, text="수정", command=lambda: self.edit(mode, k1, k2, id_)).pack(side="left")
        tk.Button(f_btn, text="삭제", command=lambda: self.delete(mode)).pack(side="left")
        
        tree.bind("<<TreeviewSelect>>", lambda e: self.on_select(tree, k1, k2, id_))

    def on_select(self, tree, k1, k2, id_):
        sel = tree.selection()
        if sel:
            v = tree.item(sel[0])['values']
            k1.delete(0, tk.END); k1.insert(0, v[0])
            k2.delete(0, tk.END); k2.insert(0, v[1] if v[1] != 'None' else '')
            id_.delete(0, tk.END); id_.insert(0, v[2])

    def add(self, mode, k1, k2, id_):
        tree = getattr(self, f"tree_{mode}")
        if k1.get() and id_.get():
            tree.insert("", "end", values=(k1.get(), k2.get(), id_.get(), 0))
            self.save_cfg()
            k1.delete(0, tk.END); k2.delete(0, tk.END); id_.delete(0, tk.END)

    def edit(self, mode, k1, k2, id_):
        tree = getattr(self, f"tree_{mode}")
        sel = tree.selection()
        if sel and k1.get():
            cnt = tree.item(sel[0])['values'][3]
            tree.item(sel[0], values=(k1.get(), k2.get(), id_.get(), cnt))
            self.save_cfg()

    def delete(self, mode):
        tree = getattr(self, f"tree_{mode}")
        for s in tree.selection(): tree.delete(s)
        self.save_cfg()

    def save_cfg(self):
        self.config["min_time_min"] = int(self.e_min.get())
        self.config["max_time_min"] = int(self.e_max.get())
        self.config["mode"] = self.combo.get()
        self.config["smart_schedule"] = self.var_smart.get()
        self.config["include_ads"] = self.var_ads.get()
        
        for m in ["shopping", "blog"]:
            t = getattr(self, f"tree_{m}")
            lst = []
            for i in t.get_children():
                v = t.item(i)['values']
                lst.append({"keyword":str(v[0]), "keyword_2":str(v[1]) if str(v[1]) != 'None' else '', "id":str(v[2]), "success_count":int(v[3])})
            self.config[f"targets_{m}"] = lst
        ConfigManager.save(self.config)

    def toggle(self):
        if self.logic.is_running:
            self.logic.is_running = False
            self.log("중단 요청...")
        else:
            self.save_cfg()
            self.logic.is_running = True
            min_t = int(self.e_min.get())
            max_t = int(self.e_max.get())
            mode = self.combo.get()
            
            if self.var_integrated.get():
                # 통합 모드
                ts = self.config.get("targets_shopping", [])
                tb = self.config.get("targets_blog", [])
                if not ts and not tb:
                     messagebox.showerror("Err", "타겟이 없습니다.")
                     self.logic.is_running = False
                     return
                self.log("<<< 통합 자동화 모드 시작 >>>")
                threading.Thread(target=self.logic.run_wrapper, args=(self.logic.run_integrated_loop, ts, tb, min_t, max_t, mode), daemon=True).start()
            else:
                # 단일 모드
                work = "shopping" if self.notebook.index("current") == 0 else "blog"
                targets = self.config.get(f"targets_{work}", [])
                if not targets:
                    messagebox.showerror("Err", f"{work} 타겟 없음")
                    self.logic.is_running = False
                    return
                threading.Thread(target=self.logic.run_wrapper, args=(self.logic.run_cycle_loop, targets, min_t, max_t, mode, work), daemon=True).start()

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def on_success_ui(self, t_id):
        self.root.after(0, lambda: self.update_cnt(t_id))

    def update_cnt(self, t_id):
        for m in ["shopping", "blog"]:
            t = getattr(self, f"tree_{m}")
            for i in t.get_children():
                v = t.item(i)['values']
                if str(v[2]) == str(t_id):
                    new_c = int(v[3]) + 1
                    t.item(i, values=(v[0], v[1], v[2], new_c))
                    self.save_cfg()
                    return

def main(expiration_date=None):
    try:
        root = tk.Tk()
        app = BotApp(root, expiration_date)
        root.mainloop()
    except Exception as e: print(e)

if __name__ == "__main__":
    main()
