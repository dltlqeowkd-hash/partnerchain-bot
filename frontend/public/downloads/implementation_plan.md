
# Goal Description
Update the bot to simulate extremely human-like behavior on Naver:
1.  **Naver Fake Search**: Perform 1-3 random searches *on Naver* before the target search to build a history.
2.  **Logic Update**:
    - **Remove** specific Tab clicks (VIEW/Blog).
    - **Instead**, scroll the Main Search (Integrated) page and click "검색결과 더보기" (More Results) for the relevant section (VIEW/SmartBlock).
3.  **Humanization**:
    - **Always** scroll 1-3 times naturally *before* clicking the target blog post.
    - **Always** scroll 1-3 times naturally *before* clicking the sales link.
4.  **Sales Link Detection**:
    - Support finding links hidden in "Smart Editor" cards (`se-oglink`) by matching the title/summary text provided by the user (as "Link Identifier").

## User Review Required
None.

## Proposed Changes
### `multi_bot/multi_bot.py`
#### [MODIFY] `search_and_find_blog`
- **Pre-Search**: Add loop for 1-3 `GENERIC_KEYWORDS` searches -> Scroll -> Back to Main.
- **Search Flow**:
    - Type 1st Keyword.
    - **Scroll Loop**: instead of clicking tabs, scroll down looking for `VIEW` header or `SmartBlock`.
    - Find "More Results" (더보기) button for that section and click it.
    - **Target Finding**:
        - Use existing Fallback (Text/CSS).
        - **Before Click**: `human_scroll(random(1,3))` -> `smooth_move` -> Click.
- **Post-Enty Logic**:
    - Scroll read.
    - **Sales Link**:
        - Add logic to find `.se-oglink-info-container` or `a.se-oglink-thumbnail`.
        - Check text in `strong`, `p` tags inside.
        - **Before Click**: `human_scroll(random(1,3))` -> `smooth_move` -> Click.

## Verification Plan
### Manual Verification
1.  Watch the bot perform "Fake Searches" on Naver.
2.  Watch it scroll the main page and click "More Results" instead of the top tab.
3.  Observe the "hesitation" (scroll) before clicking the target blog.
4.  Verify it correctly identifies and clicks the link card when "AOHi" or similar text is used as the identifier.
