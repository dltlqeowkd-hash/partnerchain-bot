from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random

class CoupangScraper:
    def __init__(self, log_func=print):
        self.log = log_func
        self.driver = None

    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        # 쿠팡은 User-Agent 관리가 매우 중요
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        options.add_argument("accept-language=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(r'd:\bot\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
            self.log(f"[Coupang] '{keyword}' 사람처럼 검색 준비...")
            
            # 1. 메인 이동
            self.driver.get("https://www.coupang.com")
            time.sleep(random.uniform(2, 4))
            
            # 2. 검색창 찾기 & 타이핑
            try:
                search_box = self.driver.find_element(By.ID, "headerSearchKeyword")
                search_box.click()
                time.sleep(0.5)
                self.human_typing(search_box, keyword)
                time.sleep(0.5)
                search_box.send_keys(Keys.RETURN)
            except:
                self.log("쿠팡 검색창 찾기 실패, 직접 이동 시도")
                url = f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user"
                self.driver.get(url)

            time.sleep(random.uniform(2, 3))
            
            # 상품 리스트
            items = self.driver.find_elements(By.CLASS_NAME, "search-product")
            
            target_links = []
            for i, item in enumerate(items):
                if i >= max_items: break
                try:
                    name = item.find_element(By.CLASS_NAME, "name").text
                    price = item.find_element(By.CLASS_NAME, "price-value").text
                    link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    try: img = item.find_element(By.CLASS_NAME, "search-product-wrap-img").get_attribute("src")
                    except: img = ""
                    
                    # 로켓상품만 필터링 하거나 등등의 옵션 가능. 일단 다 수집.
                    target_links.append({
                        "title": name,
                        "link": link,
                        "price": price,
                        "image": img,
                        "source": "Coupang"
                    })
                except: continue
                
            self.log(f"[Coupang] {len(target_links)}개 상품 상세 분석 시작...")
            
            for info in target_links:
                try:
                    self.log(f" > 분석 중: {info['title'][:15]}...")
                    full_data = self.scrape_detail(info, max_reviews)
                    results.append(full_data)
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    self.log(f"ERROR: {e}")
                    
        except Exception as e:
            self.log(f"Coupang Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        return results

    def scrape_detail(self, item_info, max_reviews):
        # 쿠팡 상세페이지
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        try:
            self.driver.get(item_info['link'])
            time.sleep(2)
            
            # 스크롤로 리뷰 로딩 유도
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
            
            # 상품평 탭 클릭 (필요시) - 쿠팡은 보통 스크롤만 내려도 아래에 있음.
            # 상세한 리뷰 긁기는 '상품평' 버튼을 눌러야 함.
            reviews = []
            try:
                # 상품평 탭 찾기
                # 보통 h2 타이틀 '상품평' 근처 혹은 탭
                # 간단하게는 화면에 보이는 베스트 리뷰 몇개만 가져오기
                
                review_articles = self.driver.find_elements(By.CLASS_NAME, "sdp-review__article__list__review__content")
                
                for i, r in enumerate(review_articles):
                    if i >= max_reviews: break
                    reviews.append(r.text.strip())
                    
                # 만약 부족하면 '상품평 보기' 클릭 로직 추가 필요 (복잡도 증가)
                
            except: pass
            
            item_info['reviews'] = reviews
            item_info['review_count'] = len(reviews)
            
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        return item_info
