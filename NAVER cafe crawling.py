from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def collect_article_content(driver):
    try:
        main_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div'))
        )
        return main_element.get_attribute('innerText')
    except:
        try:
            main_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div'))
            )
            return main_element.get_attribute('innerText')
        except:
            return None

# 크롬 드라이버 설정
driver = webdriver.Chrome()

# 네이버 로그인 페이지로 이동
url = 'https://nid.naver.com/nidlogin.login'
driver.get(url)
time.sleep(3)

print("로그인 수동으로 진행 후, 다시 카페 페이지로 이동합니다.")
time.sleep(12)  # 로그인을 직접 수행할 시간을 줍니다.

cafe_url = 'https://cafe.naver.com/suhui'
driver.get(cafe_url)
time.sleep(3)

# 검색어 리스트 설정
search_keywords = ['고려대 면접']


results = []

# 키워드별로 검색 수행
for keyword in search_keywords:
    try:

        driver.get(cafe_url)  # 카페 페이지로 재접속
        time.sleep(3)


        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'topLayerQueryInput'))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys("\n")
        time.sleep(2)


        driver.switch_to.frame("cafe_main")


        search_option_dropdown2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "divSearchMenuTop"))
        )
        search_option_dropdown2.click()
        time.sleep(1)

        interview_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '┗면접+논술 후기')]"))
        )
        interview_option.click()
        time.sleep(2)

    except Exception as e:
        print(f"키워드 '{keyword}'에 대한 검색 또는 옵션 설정 오류: {e}")
        continue


    try:
        search_option_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "divSearchByTop"))
        )
        search_option_dropdown.click()
        time.sleep(1)

        title_only_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '제목만')]"))
        )
        title_only_option.click()
        time.sleep(2)


        search_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '검색')]"))
        )
        search_btn.click()
        time.sleep(2)


        dropdown_menu = driver.find_element(By.ID, "listSizeSelectDiv")
        dropdown_menu.click()
        time.sleep(1)

        fifty_option = driver.find_element(By.XPATH, "//a[contains(text(), '50개씩')]")
        fifty_option.click()
        time.sleep(2)

    except Exception as e:
        print(f"제목만 옵션 설정 오류: {e}")
        continue


    while True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.select('div.inner_list a.article')
            links = ['https://cafe.naver.com' + article['href'] for article in articles]

            if not links:
                print("더 이상 게시글이 없습니다.")
                break

            # 게시글 내용을 순차적으로 방문하여 수집
            for link in links:
                driver.get(link)
                time.sleep(3)


                try:
                    driver.switch_to.frame("cafe_main")
                except Exception as e:
                    print(f"iframe 전환 오류: {e}")
                    continue

                soup_article = BeautifulSoup(driver.page_source, 'html.parser')


                try:
                    title = soup_article.find('h3', class_='title_text').text.strip()
                except:
                    title = 'N/A'


                try:
                    nickname_div = soup_article.find('div', class_='article_writer')
                    if nickname_div is not None:
                        nickname_strong = nickname_div.find('strong', class_='user')
                        nickname = nickname_strong.text.strip() if nickname_strong else 'N/A'
                    else:
                        nickname = 'N/A'
                except:
                    nickname = 'N/A'


                try:
                    date = soup_article.find('div', class_='article_info').find('span', class_='date').text.strip()
                except:
                    date = 'N/A'


                content = collect_article_content(driver)
                if content is None:
                    content = '내용을 수집할 수 없습니다.'

                result = {
                    'Keyword': keyword,
                    'Link': link,
                    'Title': title,
                    'Nickname': nickname,
                    'Date': date,
                    'Content': content
                }
                results.append(result)


            try:
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='prev-next']//a[contains(text(), '>')]"))
                )
                next_page.click()
                time.sleep(3)
            except:
                print("더 이상 다음 페이지가 없습니다.")
                break

        except Exception as e:
            print(f"오류 발생: {e}")
            break


df = pd.DataFrame(results)


df.to_csv('NAVER_Cafe_crawling.csv', index=False, encoding='utf-8-sig')


driver.quit()

print("데이터 수집 및 CSV 저장 완료.")
