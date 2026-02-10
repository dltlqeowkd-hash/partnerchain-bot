# Naver Multi-Bot Refinement Task List

- [x] **Revert to v4.2 Secure Commercial Version** (Restored based on user request & screenshot)
    - [x] Restore UI (Company Name, Integrated Cycle Checkbox, Smart Schedule)
    - [x] Restore Logic (Integrated Loop, Blog Tab Switch Fix)

- [/] Refine Blog Mode Search Logic
    - [ ] Implement `click_more_results` helper function (Search Result More).
    - [ ] Implement 1st Keyword Search -> Scroll (Max 10) loop.
    - [ ] Implement Fallback to 2nd Keyword if 1st fails.
- [ ] Refine Blog Post Interaction
    - [ ] Implement "Read to bottom" logic.
    - [ ] Implement Random Action: "Save (Keep)" OR "Share -> Copy Link".
    - [ ] Find and Click Sales Link (using Link ID).
- [ ] Refine Product Page Interaction
    - [ ] Implement Gallery Image Swipe (Next/Prev or Click Thumbnails).
    - [ ] Implement "Expand Detail" (already exists, verify).
    - [ ] Implement "Scroll to bottom".
    - [ ] Implement Random Action: Review OR Q&A Click.
- [ ] Verify Common Features
    - [ ] Ensure `human_typing` is used for all text inputs.
    - [ ] Verify Browser Cleanup (Cookies/Close) at cycle end.
