
# Multi-Mode Bot Walkthrough

## Overview
This bot has been upgraded to support multiple operation modes via a Tab-based interface.
- **Shopping Mode**: Standard Naver Shopping search and interaction.
- **Blog Mode**: Search via Blogs/VIEW tab, read blog posts, find target link, and then interact with the target product.

## New Features
10. **Tab Interface**: switch between "Shopping" and "Blog" tabs.
11. **Blog Logic (Enhanced)**:
12.    - **Fake Search**: Performs 1-3 random searches on Naver Main to build history before the real search.
13.    - **Natural Navigation**: Instead of clicking tabs, it scrolls down and clicks "More Results" (검색결과 더보기) just like a human.
14.    - **Hesitation**: Delays and scrolls naturally before clicking the target blog or sales link.
15.    - **Fallback Search**: If title click fails, searches for text and clicks.
16. **Smart Link Detection**: Finds sales links even if they are embedded in Smart Editor cards (using title/description text).
17. **Contextual Actions**: Reads to bottom, performs random Share/Save actions, and keeps cookies clean per cycle.
18. **Active Idle**: During the product reading phase, the bot continuously scrolls up/down and moves the mouse (no static waiting).
19. **Real-time Timer**: Displays the remaining time for the current cycle in the UI.

## Usage
1. Run `launcher.py` or the built executable.
2. Select the desired tab (Shopping or Blog).
3. Add Keywords/IDs.
   - **Shopping**: 1st Keyword = Search Term, ID = Product ID.
   - **Blog**: 1st Keyword = Search Term (Naver), 2nd Keyword = Blog Title Keyword, ID = Part of the target linkURL (e.g., 'smartstore' or product ID).
4. Click START. The bot will execute the logic corresponding to the *currently active tab*.

### **📝 Blog/Viral Mode Input Guide**
- **1st Keyword**: The search term to enter on Naver main page (e.g., `USB4 2.0 케이블`).
- **2nd Keyword**: A unique word or phrase contained in your target blog post's title. The bot scrolls through the search results and clicks the post that contains this keyword (e.g., `AOHI`).
- **Product ID / Link Identifier**: A unique string found in the final sales link URL within the blog post.
    - If the link is `https://smartstore.naver.com/shop/products/12345678`, enter `12345678`.
    - If the link is a shortened URL or tracking link, enter a unique part of that URL (e.g., `bit.ly/xyz` or `coupang`).
    - **Tip**: To ensure the bot clicks the correct link, use a unique part of the URL.

## File Structure
- `multi_bot/multi_bot.py`: Main logic and UI implementation.
- `multi_bot/bot_config.json`: Configurations, now supports `targets_shopping` and `targets_blog`.
