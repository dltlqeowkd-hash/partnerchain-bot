import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
import sys

# 프로젝트 루트 경로를 path에 추가하여 모듈 import 원활하게
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.naver_scraper import NaverScraper
from scrapers.coupang_scraper import CoupangScraper
from utils.excel_exporter import ExcelExporter

class SourcingBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sourcing Master Bot v1.0")
        self.root.geometry("800x600")
        
        self.is_running = False
        
        self.create_ui()
        
    def create_ui(self):
        # 1. 입력 폼 (상단)
        f_input = tk.LabelFrame(self.root, text="검색 조건")
        f_input.pack(fill="x", padx=10, pady=5)
        
        # 키워드
        tk.Label(f_input, text="제품명/키워드:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.e_keyword = tk.Entry(f_input, width=40)
        self.e_keyword.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="w")
        
        # 타겟 사이트
        tk.Label(f_input, text="분석 대상:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        f_checks = tk.Frame(f_input)
        f_checks.grid(row=1, column=1, columnspan=2, sticky="w")
        
        self.var_naver = tk.BooleanVar(value=True)
        self.var_coupang = tk.BooleanVar(value=True)
        
        tk.Checkbutton(f_checks, text="네이버 쇼핑", variable=self.var_naver).pack(side="left", padx=5)
        tk.Checkbutton(f_checks, text="쿠팡", variable=self.var_coupang).pack(side="left", padx=5)
        
        # 옵션
        tk.Label(f_input, text="수집 옵션:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.val_max_items = tk.IntVar(value=5)
        self.val_max_reviews = tk.IntVar(value=20)
        
        f_opts = tk.Frame(f_input)
        f_opts.grid(row=2, column=1, columnspan=2, sticky="w")
        
        tk.Label(f_opts, text="상위").pack(side="left")
        tk.Entry(f_opts, textvariable=self.val_max_items, width=5).pack(side="left")
        tk.Label(f_opts, text="개 상품 분석 | 상품당 리뷰 최대").pack(side="left")
        tk.Entry(f_opts, textvariable=self.val_max_reviews, width=5).pack(side="left")
        tk.Label(f_opts, text="개").pack(side="left")

        # 2. 실행 버튼
        f_btn = tk.Frame(self.root)
        f_btn.pack(fill="x", padx=10, pady=5)
        
        self.btn_run = tk.Button(f_btn, text="시장 조사 시작", command=self.start_analysis, bg="#4CAF50", fg="white", font=("Bold", 12), height=2)
        self.btn_run.pack(fill="x")
        
        # 3. 로그
        self.log_area = scrolledtext.ScrolledText(self.root, height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)
        
    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)
        
    def start_analysis(self):
        if self.is_running:
            return
            
        keyword = self.e_keyword.get().strip()
        if not keyword:
            messagebox.showwarning("입력 오류", "검색할 키워드를 입력해주세요.")
            return
            
        self.is_running = True
        self.btn_run.config(text="분석 중... (잠시만 기다려주세요)", state="disabled")
        
        # 스레드로 작업 시작
        threading.Thread(target=self.run_process, args=(keyword,), daemon=True).start()
        
    def run_process(self, keyword):
        try:
            self.log(f"'{keyword}' 시장 조사를 시작합니다...")
            max_items = self.val_max_items.get()
            max_reviews = self.val_max_reviews.get()
            
            use_naver = self.var_naver.get()
            use_coupang = self.var_coupang.get()
            
            if not use_naver and not use_coupang:
                self.log("선택된 플랫폼이 없습니다.")
                return

            all_data = []

            # 1. Naver Scraper
            if use_naver:
                self.log("=== 네이버 쇼핑 스캔 시작 ===")
                try:
                    ns = NaverScraper(self.log)
                    results = ns.search(keyword, max_items, max_reviews)
                    all_data.extend(results)
                    self.log(f"네이버 스캔 완료: {len(results)}개 상품 수집")
                except Exception as e:
                    self.log(f"네이버 스크래핑 실패: {e}")
                
            # 2. Coupang Scraper
            if use_coupang:
                self.log("=== 쿠팡 스캔 시작 ===")
                try:
                    cs = CoupangScraper(self.log)
                    results = cs.search(keyword, max_items, max_reviews)
                    all_data.extend(results)
                    self.log(f"쿠팡 스캔 완료: {len(results)}개 상품 수집")
                except Exception as e:
                    self.log(f"쿠팡 스크래핑 실패: {e}")
                
            if not all_data:
                self.log("수집된 데이터가 없습니다.")
                return

            self.log("데이터 분석 및 리포트 생성 중...")
            
            # Excel Export
            report_path = ExcelExporter.save_report(keyword, all_data)
            
            self.log(f"✅ 리포트 생성 완료!")
            self.log(f"파일 경로: {report_path}")
            
            # 파일 자동 실행 (Windows)
            try:
                os.startfile(report_path)
            except: pass
            
        except Exception as e:
            self.log(f"Critical Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_run.config(text="시장 조사 시작", state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SourcingBotApp(root)
    root.mainloop()
