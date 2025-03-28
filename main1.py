from playwright.sync_api import sync_playwright
import time
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

# 讀取環境變數
load_dotenv()
username = os.getenv("username")
password = os.getenv("password")

# 設定網址
url = "https://www.facebook.com"
reel_url = "https://www.facebook.com/reel/"
cookies_file = "fb_cookies.txt"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
                                # channel="chrome",
                                args=["--start-maximized"])
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    page = context.new_page()
    
    # 載入 Cookies
    if os.path.exists(cookies_file):
        print("找到 Cookies，正在載入...")
        with open(cookies_file, "r", encoding="utf-8") as file:
            cookies = json.load(file)
        context.add_cookies(cookies)
    
    # 打開 Facebook
    page.goto(url)
    time.sleep(5)
    
    # 如果沒有 Cookies，執行手動登入
    # print("手動登入中")
    # page.fill("#email", username)
    # page.fill("#pass", password)
    # page.press("#pass", "Enter")
    # time.sleep(30)  # 等待登入成功
    
    # # 登入後存 Cookies
    # cookies = context.cookies()
    # with open(cookies_file, "w", encoding="utf-8") as file:
    #     json.dump(cookies, file, ensure_ascii=False, indent=4)
    # print("Cookies 已儲存")
    
    # 檢查是否被鎖住
    if page.locator("text=你的帳號暫時被鎖住").count() > 0:
        print("帳號可能被鎖定，嘗試點擊確認")
        confirm_buttons = page.locator("text=是")
        if confirm_buttons.count() > 1:
            confirm_buttons.nth(1).click()
            print("已點擊『是』按鈕")
        else:
            print("找不到『是』按鈕，請手動處理")
    
    # 進入 Reels
    print("前往 Facebook Reels")
    page.goto(reel_url, timeout=60000)
    time.sleep(10)
    
    try:
        # 取標籤
        hashtags = page.locator("a[href*='watch/hashtag/']").all()
        hashtag_list = []
        for tag in hashtags:
            if tag.inner_text() not in hashtag_list:
                hashtag_list.append(tag.inner_text())
        print("標籤:", hashtag_list)

        # 取內文
        text_link = page.locator("div.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs.x126k92a")
        text = text_link.inner_text()
        print (f"內文: {text}")

        # profile_link = page.locator("a[aria-label*='查看擁有者個人檔案']").first
        # owner_id = profile_link.get_attribute("href")
        # print(f"Profile: {owner_id}")
        # owner_link = page.locator("h2[dir='auto']").first
        # owner_name = owner_link.inner_text()
        owner_name = page.get_by_role("heading", level=2).first.inner_text()
        print (f"發文者: {owner_name}")

        # 按讚數、留言數、分享數
        like_link = page.locator('div[aria-label="讚"]').first
        like_num = like_link.locator('xpath=following::span[contains(@class,"x1lliihq")][1]').inner_text()
        if like_num:
            print('按讚數:', like_num)
        else:
            print('按讚數:', 0)

        message_link = page.locator("div[aria-label*='留言']").first
        message_num = message_link.locator('xpath=following::span[contains(@class,"x1lliihq")][1]').inner_text()
        if message_num:
            print('留言數:', message_num)
        else:
            print('留言數:', 0)

        share_link = page.locator("div[aria-label*='分享']").first
        share_num = share_link.locator('xpath=following::span[contains(@class,"x1lliihq")][1]').inner_text()
        if share_num:
            print('分享數:', share_num)
        else:
            print('分享數:', 0)

        # 打開留言
        comment_button = page.locator("[aria-label='留言']").first
        comment_button.click()
        print("已點擊留言按鈕")

        page.wait_for_timeout(5000)

        # 將留言從『最相關』改為『所有留言』
        filter_button = page.locator("div[role='button']:has-text('最相關')")
        filter_button.click()
        print("已點擊『最相關』按鈕")
        page.wait_for_selector("div[role='menuitem']", timeout=5000)
        all_comments_option = page.locator("div[role='menuitem']:has-text('所有留言')").nth(1)
        all_comments_option.wait_for(timeout=5000)
        all_comments_option.click()
        print("已選擇『所有留言』")

        page.wait_for_timeout(3000)
        
        initial_displaye_num = 6
        per_click_load_num= 10
        # message_num = int(message_num.replace(",", ""))
        message_num = int(message_num)
        
        # 計算滾動次數
        needed_scrolls = (message_num - initial_displaye_num) // per_click_load_num
        if (message_num - initial_displaye_num) % per_click_load_num != 0:
            needed_scrolls += 1

        # 定位滾動條
        scrollbar = page.locator("div[data-thumb='1']").nth(4)
        scrollbar.bounding_box()
        box = scrollbar.bounding_box()
        if box:
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

        # 使用 count 來控制滾動次數
        for _ in range(needed_scrolls):
            more_button = page.locator("div[role='button']:has-text('查看更多留言')")
            if more_button.is_visible():
                more_button.click()
                page.wait_for_timeout(2000) 
            page.mouse.wheel(0, 5000)  
            page.wait_for_timeout(2000)

        # users = page.locator('div[role="article"] a[role="link"] span').all()
        # comments = page.locator('div[role="article"] div[dir="auto"]').all()
        # for name, comment in zip(users, comments):
        #     data.append(
        #         {"user": name.text_content(), 
        #          "comment": comment.text_content()}
        #     )

        # 抓取留言
        data = [] 
        page.wait_for_selector('div[role="article"]')
        comments = page.locator('div[role="article"]').all()
        for comment in comments:
            user_link = comment.locator('a[role="link"][tabindex="0"]').first
            user_name = user_link.locator('span').first.text_content()
            user_href = user_link.get_attribute("href")
            user_id_match = re.search(r'(?:profile\.php\?id=|/|^)(\d+)(?:&|$|/)', user_href)
            user_id = user_id_match.group(1) if user_id_match else "0" 
            # user_id = user_href.split("id=")[1].split("&")[0]

            comment_parts = comment.locator('div[dir="auto"]').all()
            comment_texts = []
            for part in comment_parts:
                part_text = part.text_content().strip()

                images = part.locator('img').all()
                for img in images:
                    img_alt = img.get_attribute("alt") or "[圖片]"
                    part_text += f" {img_alt} "

                if part_text:
                    comment_texts.append(part_text)
        
            comment_text = " ".join(comment_texts).strip() or ""

            # comment_parts = comment.locator('div[dir="auto"]').all()
            # comment_texts = []
            # for part in comment_parts:
            #     part_text = part.text_content().strip()

            #     images = part.locator('img').all()
            #     for img in images:
            #         img_alt = img.get_attribute("alt") or "[圖片]"
            #         part_text += f" {img_alt} "

            #     if part_text:
            #         comment_texts.append(part_text)
            # # 合併多段留言
            # comment_text = " ".join(comment_texts)

            data.append({
                "user": user_name,
                "userId": user_id,
                "comment": comment_text.strip()
            })
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"錯誤: {e}")
    
    browser.close()

# 約 8 小時