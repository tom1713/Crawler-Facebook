from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os
import json

# 讀取環境變數
load_dotenv()
username = os.getenv("username")
password = os.getenv("password")

# 設定 Chrome 選項
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # 移除機器人標記
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
options.add_argument("--incognito")  # 無痕模式

# 啟動瀏覽器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 設定網址
url = 'https://www.facebook.com'
reel_url = 'https://www.facebook.com/reel/'

# 打開 Facebook
driver.get(url)
time.sleep(10)

# 載入 Cookies
cookies_file = "fb_cookies.txt"
if os.path.exists(cookies_file):
    print("找到 Cookies，正在載入...")
    with open(cookies_file, "r", encoding="utf-8") as file:
        cookies = json.load(file)
    
    for cookie in cookies:
        driver.add_cookie(cookie)

    time.sleep(3)
    driver.refresh()  # 重新整理頁面以應用 Cookies
    time.sleep(10)
    print("Cookies 載入完成，嘗試自動登入！")
else:
    print("沒有 Cookies，請手動登入")
    
if "login" in driver.current_url:
    print("手動登入中")
    email_input = driver.find_element(By.ID, "email")  # 定位 Email 輸入框
    password_input = driver.find_element(By.ID, "pass")  # 定位 Password 輸入框
    
    email_input.send_keys(username)  
    password_input.send_keys(password)  
    password_input.send_keys(Keys.RETURN)  # 按 Enter 鍵登入
    
    time.sleep(30)  # 等待登入成功
    
    # 登入後存 Cookies
    cookies = driver.get_cookies()
    with open(cookies_file, "w", encoding="utf-8") as file:
        json.dump(cookies, file, ensure_ascii=False, indent=4)
    
    print("Cookies 已儲存")

# 確認是否被鎖住
if len(driver.find_elements(By.XPATH, "//*[contains(text(), '你的帳號暫時被鎖住')]")) > 0:
    print("帳號可能被鎖定，嘗試點擊確認")
    
    # 嘗試點擊「是」按鈕
    confirm_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), '是')]")
    
    if len(confirm_buttons) > 1:
        confirm_buttons[1].click()
        print("已點擊『是』按鈕")
    else:
        print("找不到『是』按鈕，請手動處理")

# 進入 Reels
print("前往 Facebook Reels")
driver.get(reel_url)
time.sleep(10)
print("進入 Facebook Reels")

driver.quit() # 關閉瀏覽器

### 約1.5hr