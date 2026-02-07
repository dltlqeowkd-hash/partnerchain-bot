from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from tkinter import messagebox

class NaverScraper:
    def __init__(self, log_func=print):
        self.log = log_func
        self.driver = None
        
    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless") # 디버깅 위해 헤드리스 끔
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # d:\bot\chromedriver.exe (기존 경로 활용)
        service = Service(r'd:\bot\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1280, 800)
        
    def human_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            
    def search(self, keyword, max_items=5, max_reviews=10):
        if not self.driver:
            self.setup_driver()
            
        results = []
        try:
            self.log(f"[Naver] '{keyword}' 메인 우회 검색 준비...")
            
            # 1. 네이버 메인 이동 (쇼핑몰 직접 접속 피함)
            self.driver.get("https://www.naver.com")
            time.sleep(random.uniform(2, 3))
            
            # 2. 메인 검색창 찾기 & 타이핑
            try:
                search = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "query"))
                )
                search.click()
                time.sleep(0.5)
                self.human_typing(search, keyword)
                time.sleep(0.5)
                search.send_keys(Keys.RETURN)
            except Exception as e:
                self.log(f"메인 검색 실패: {e}")
                return []
                
            time.sleep(2)
            
            # 3. '쇼핑' 탭 클릭
            try:
                self.log("쇼핑 탭 진입 시도...")
                # PC 버전 기준 쇼핑 탭 찾기
                shopping_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), '쇼핑') and contains(@class, 'tab')]")
                shopping_btn.click()
            except:
                # 탭이 안 보이면 '더보기'를 눌러야 할 수도 있음 (생략하고 URL Fallback)
                self.log("쇼핑 탭 클릭 실패, 직접 URL로 이동")
                self.driver.get(f"https://search.shopping.naver.com/search/all?query={keyword}")
            
            time.sleep(3)
            
            # 4. 보안 절차(Captcha) 감지 및 수동 해결 대기
            if "security" in self.driver.current_url or "captcha" in self.driver.page_source:
                self.log("!! 보안 절차(Captcha) 감지됨 !!")
                messagebox.showinfo("보안 확인 필요", "브라우저에 뜬 보안 문자(이미지 등)를 직접 해결해 주세요.\n해결 후 [확인]을 누르면 봇이 계속 진행합니다.")
                self.log("보안 절차 해결 확인 완료. 재개합니다.")
                time.sleep(2)
            
            # 스크롤 조금 내려서 로딩
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
            
            # 아이템 리스트 확보 (광고 제외하고 일반 상품 위주로)
            # basicList_item__ 류의 클래스 찾기
            items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'basicList_item__')]")
            
            target_links = []
            for i, item in enumerate(items):
                if i >= max_items: break
                try:
                    title_el = item.find_element(By.XPATH, ".//a[contains(@class, 'basicList_link__')]")
                    title = title_el.text
                    link = title_el.get_attribute('href')
                    
                    try:
                        price = item.find_element(By.XPATH, ".//span[contains(@class, 'price_num__')]").text
                    except: price = "0"
                    
                    try:
                        img = item.find_element(By.XPATH, ".//div[contains(@class, 'basicList_img__')]//img").get_attribute('src')
                    except: img = ""
                    
                    target_links.append({
                        "title": title,
                        "link": link,
                        "price": price,
                        "image": img,
                        "source": "Naver"
                    })
                except Exception as e:
                    print(f"Item parsing error: {e}")
                    
            self.log(f"[Naver] {len(target_links)}개 상품 상세 분석 시작...")
            
            # 상세 페이지 진입
            for info in target_links:
                try:
                    self.log(f" > 분석 중: {info['title'][:15]}...")
                    full_data = self.scrape_detail(info, max_reviews)
                    results.append(full_data)
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    self.log(f"ERROR: {e}")
                    
        except Exception as e:
            self.log(f"Naver Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
        return results
        
    def scrape_detail(self, item_info, max_reviews):
        # 탭 윈도우 관리 필요
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        try:
            self.driver.get(item_info['link'])
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 5)
            
            # 리뷰 탭 클릭 (네이버 스마트스토어 기준)
            # 구조가 다양해서 try-except로 여러 케이스 대응 필요
            reviews = []
            try:
                # 1. 스마트스토어
                review_tab = self.driver.find_elements(By.XPATH, "//*[contains(text(), '리뷰') or contains(text(), '구매평')]")
                if review_tab:
                    clicked = False
                    for tab in review_tab:
                        try:
                            tab.click()
                            clicked = True
                            break
                        except: continue
                    
                    if clicked:
                        time.sleep(1)
                        # 리뷰 텍스트 수집
                        review_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'review_text')]")  # 클래스명은 변동 가능성 큼, 범용적으로 수정 필요
                        if not review_items:
                            # 다른 구조 시도 (스마트스토어 최신 UI)
                            review_items = self.driver.find_elements(By.CSS_SELECTOR, "div.reviewItems_text__XIsTc") # 예시 클래스
                            
                        # 범용 XPATH
                        if not review_items:
                             review_items = self.driver.find_elements(By.XPATH, "//ul//li//div//span[string-length(text()) > 10]")

                        for r_idx, r in enumerate(review_items):
                            if r_idx >= max_reviews: break
                            reviews.append(r.text.strip())
            except Exception as e:
                self.log(f"리뷰 수집 실패: {e}")
                
            item_info['reviews'] = reviews
            item_info['review_count'] = len(reviews) # 실제 수집된 개수 (전체 개수는 아님)
            
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        return item_info
