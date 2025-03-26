from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
# options.add_argument("window-size=1920,1080")
# options.add_argument("--headless") # 無頭模式


# 啟動瀏覽器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 設定網址
url = 'https://www.facebook.com'
reel_url = 'https://www.facebook.com/reel/'

# 打開 Facebook
driver.get(url)
time.sleep(5)

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
    print("Cookies 載入完成")
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
print("進入 Facebook Reels")
time.sleep(30)

try:
    # 打開留言
    comment_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='留言']")))
    comment_button.click()
    print("已點擊留言按鈕")
    time.sleep(15)
    
    owner_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@aria-label, '查看擁有者個人檔案')]")))
    owner_name = owner_link.text  # 發文者名稱
    owner_id = owner_link.get_attribute("href")  # 取得完整的網址
    owner_id = owner_id.split("id=")[-1].split("&")[0]  # 擷取 ID
    print(f"發文者: {owner_name}, ID: {owner_id}")

    hashtags = driver.find_elements(By.XPATH, "//a[contains(@href, 'watch/hashtag/')]")
    hashtag_list = [tag.text for tag in hashtags]
    print("標籤:", hashtag_list)

except Exception as e:
    print(f"錯誤: {e}")




# 等待頁面完全加載，直到發文者的元素可見
# try:
#     # 發文者
#     author_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="查看擁有者個人檔案"]')))
#     author_name = author_element.text
#     author_name_elements = driver.find_elements(By.XPATH, '//a[@aria-label="查看擁有者個人檔案"]')
#     author_profileUrl = author_element.get_attribute('href')
#     print(f"發文者名稱: {author_name}")
#     print(f"個人檔案 URL: {author_profileUrl}")

#     # 標籤
#     WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/watch/hashtag/")]')))
#     tag_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/watch/hashtag/")]')
#     tags = [tag.text for tag in tag_elements]
#     print(f"標籤: {tags}")

#     # 內文
#     post_text_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xdj266r')]")))
#     post_text = post_text_element.text
#     print(f"發文內文: {post_text}")

#     # 抓取數量
#     number_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'x1lliihq')]")
#     numbers = [element.text for element in number_elements]
    
#     print(f"抓取到的數字: {numbers}")
    
# except Exception as e:
#     print(f"錯誤: {e}")

driver.quit() # 關閉瀏覽器

### 約2hr