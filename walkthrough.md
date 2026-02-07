# UI Enhancement: Editable Keywords and Product ID

I have updated the Naver Shopping Bot UI to allow you to easily edit existing target keywords and product IDs.

## Changes Made

1.  **"수정" (Modify) Button**: Added a new button next to "추가" (Add) and "삭제" (Delete).
2.  **Auto-fill on Selection**: When you click on an item in the list, its 1st Keyword, 2nd Keyword, and Product ID will automatically appear in the input boxes.
3.  **Update Logic**: Clicking "수정" will update the selected item with the new values from the input boxes.

## How to Use

1.  **Select an Item**: Click on a row in the "타겟 키워드 관리" list.
2.  **Edit Values**: The values will appear in the input fields above. Change them as needed.
3.  **Click Update**: Click the **"수정"** button to save changes.

## Verification

The code has been updated and syntax checked. You can run the bot as usual:

```bash
python final_bot.py
```

Or use the `start_bot.bat` script.
