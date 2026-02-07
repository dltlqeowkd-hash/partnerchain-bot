import pandas as pd
import os
from datetime import datetime

class ExcelExporter:
    @staticmethod
    def save_report(keyword, data):
        # data format: list of dicts with 'title', 'price', 'link', 'reviews' list
        
        # 1. Summary Sheet
        summary_rows = []
        all_reviews = []
        
        for item in data:
            # Summary용
            summary_rows.append({
                "Source": item.get('source', 'Unknown'),
                "Title": item.get('title', ''),
                "Price": item.get('price', ''),
                "Review Count": item.get('review_count', 0),
                "Link": item.get('link', '')
            })
            
            # Review용
            for r in item.get('reviews', []):
                all_reviews.append({
                    "Product": item.get('title', '')[:30],
                    "Source": item.get('source', ''),
                    "Review Text": r,
                    "Link": item.get('link', '')
                })
                
        df_summary = pd.DataFrame(summary_rows)
        df_reviews = pd.DataFrame(all_reviews)
        
        # 파일명 생성
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_{keyword}_{ts}.xlsx"
        path = os.path.join(os.getcwd(), filename)
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Products', index=False)
            df_reviews.to_excel(writer, sheet_name='All Reviews', index=False)
            
        return path
