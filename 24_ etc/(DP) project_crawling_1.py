import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



pd.set_option('display.max_columns', None)  # 모든 열 출력하게끔 세팅
pd.set_option('display.max_rows', None)  # 모든 행 출력하게끔 세팅


# URL 설정
url = 'https://zigzag.kr/categories/-1?title=%ED%8C%AC%EC%B8%A0&category_id=-1&middle_category_id=547&sub_category_id=551&sort=201'  # 지그재그 와이드팬츠,리뷰많은 순

# 드라이버 설정
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))  # 자동으로 크롬 드라이버 설치 및 실행
driver.get(url)  # Chrome 브라우저에서 지정된 URL이동

# 데이터프레임을 위한 리스트 초기화
name = []  # 상품명
price = []  # 상품가격
sale_ratio = []  # 할인율
review_ratio = []  # 리뷰 점수
review_number = []  # 리뷰 개수
thumbnail = []  # 썸네일 이미지 링크
href_values = []  # 상품 상세 페이지 링크

# 수집할 data-index 값
collected_html = {}  # html 데이터를 저장할 수 있는 빈 딕셔너리 생성
collected_indices = set()  # 중복을 피하기 위해 set 사용



# 스크롤을 통해 페이지 로드
for _ in range(10):  # 스크롤 횟수를 늘림
    driver.execute_script("window.scrollBy(0, 500);")  # 500픽셀씩 스크롤
    # 스크롤 후 새로운 콘텐츠가 로드될 때까지 최대 2초간 대기
    WebDriverWait(driver, 2).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'div[data-index]')))
    # 'div[data-index]' 요소가 나타날 때까지 기다리며, 페이지 로딩 상태를 확인

    # 현재 페이지의 HTML 파싱
    soup = BeautifulSoup(driver.page_source,"html.parser")  # selenium을 통해 로드된 웹페이지에서 html을 추출하고, BeatifulSoup을 사용해 html을 파싱하여 soup 객체에 저장하는 역하
    virtuoso_div = soup.find('div', {'data-test-id': 'virtuoso-item-list'})  # div 태그를 찾자. div 태그가 속성 data-test-id를 가지며, 그 값이 'virtuoso-item-list'인 요소를 찾는다
    if virtuoso_div:  # virtuoso가 유효한 요소인지 판단
        # data-index 안 html 태그 모두 수집하기
        divs = virtuoso_div.find_all('div', {'data-index': True})  # virtuoso 내에서 조건에 맞는 모든 div 태그를 찾는 함수 # virtuoso 내부에서 data-index 속성을 가진 모든 div 태그를 찾아 divs 리스트에
        for div in divs:
            data_index = int(div['data-index'])  # data-index 값을 정수로 변환
            if data_index not in collected_indices and 0 <= data_index <= 9:
                collected_indices.add(data_index)  # set에 추가
                collected_html[data_index] = str(div)
                # data-index에 해당하는 HTML 태그 저장
            if len(collected_indices) >= 10:  # 0부터 9까지 모두 수집 시 종료
                break
    if len(collected_indices) >= 10:  # 0부터 9까지의 index를 모두 수집하면 종료
        break

# 0부터 9까지의 collected_html에서 데이터 추출
for index in range(10):
    html_content = collected_html[index]  # data-index에 해당하는 collected html가져오기
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(html_content, 'html.parser')

    # 상품 제목을 product-card 클래스에서 하나씩 추출
    product_cards = soup.find_all('div', class_='product-card css-79elbk')  # product-card 클래스 찾기
    # class = 'css-79elbx'인 모든 div 태그를 찾아 product_cards에 저장
    for card in product_cards:
        p_tag = card.find('p', class_='zds4_1kdomrc zds4_1kdomra')  # 상품 제목 찾기 #각 카드 안에서 class_='zds4_1kdomrc zds4_1kdomra'인 p 태그를 찾는다
        title = p_tag.get_text() if p_tag else "N/A"  # 태그가 없을 경우 "N/A" # p.tage가 있으면 그 안에 텍스트를 추출하고, 없으면 "N/A"를 사용
        name.append(title)  # 제목을 리스트에 추가

        # 가격
        span_price_tags = card.find_all('span',class_='zds4_s96ru86 zds4_s96ru8w zds4_1jsf80i3 zds4_1jsf80i5')  # 가격 태그 찾기 # 'span_price_tags' 변수에 가격 정보를 담고 있는 span 태그 찾기 # 'find_all' 메소드는 주어진 클래스명을 가진 모든 요소를 리스트 형태로 반환
        price_list = [span_tag.get_text() for span_tag in span_price_tags] if span_price_tags else [
            "N/A"]  # 태그가 없을 경우 "N/A" # span_price_tags가 존재하는 경우, 각 태그에서 텍스트를 추출하여 'price_list'에 저장 # 'get_text()' 메소드를 통해 텍스트 얻기
        price.append(price_list)  # 가격을 리스트에 추가

        # 할인율
        span_tags = card.find_all('span',class_='zds4_s96ru86 zds4_s96ru8w zds4_1jsf80i2')  # 할인율 태그 찾기 # 'span_tags' 변수에 할인율 정보를 담고 있는 span 태그를 찾기
        discount = [span_tag.get_text() for span_tag in span_tags] if span_tags else ["0%"]  # 태그가 없을 경우 "N/A" # span_tags가 존재하는 경우, 각 태그에서 텍스트를 추출하여 'discount' 리스트에 저장
        sale_ratio.append(discount)  # 할인율을 리스트에 추가

        # 리뷰 점수
        span_reviewscore_tags = card.find_all('span', class_='zds4_s96ru86 zds4_s96ru81h zds4_1rbzv5c4')  # 리뷰점수 태그 찾기 # class명 해당 것인 'span'태그의 모든 요소를 리스트로 반환해 저장
        review_score = [reviewscore_tag.get_text() for reviewscore_tag in
                        span_reviewscore_tags] if span_reviewscore_tags else ["N/A"]  # 태그가 없을 경우 "N/A" # 'get_text()' 메소드를 통해 텍스트 얻기
        review_ratio.append(review_score)  # 리뷰점수를 리스트에 추가

        # 리뷰 개수
        span_reviewnum_tags = card.find_all('span', class_='zds4_s96ru86 zds4_s96ru81i zds4_1rbzv5c5')  # 리뷰개수 태그 찾기 # class명 해당 것인 'span'태그의 모든 요소를 리스트로 반환해 저장
        review_num = [reviewnum_tag.get_text() for reviewnum_tag in span_reviewnum_tags] if span_reviewnum_tags else ["N/A"]  # 태그가 없을 경우 "N/A"
        review_number.append(review_num)  # 리뷰 개수를 리스트에 추가

        # 이미지 링크
        image_tags = card.find_all('img', class_='zds4_11053yc2')  # 이미지 태그찾기 # class명 해당 것인 'img'태그의 모든 요소를 리스트로 반환해 저장
        image_links = [img.get('src') for img in image_tags] if image_tags else ["N/A"]  # 이미지 링크가 없을 경우 "N/A"
        thumbnail.append(image_links)  # 이미지 링크를 리스트에 추가

        # 상품 상세 페이지 링크 수집: 리뷰 데이터 수집 위해 썸네일 마다 링크를 미리 리스트에 수집
        href_links = card.find_all('a', class_='css-152zj1o product-card-link')  # 상품 상세 링크 태그 찾기 # class명 해당 것인 'a'태그의 모든 요소를 리스트로 반환해 저장
        href_value = [a.get('href') for a in href_links] if href_links else ["N/A"]  # 링크 없으면 "N/A"
        print(href_value)
        href_values.append(href_value)  # 상세 페이지 링크를 리스트에 추가


# 데이터프레임 생성
product_info = pd.DataFrame({
    'name': name,
    'price': price,
    'sale_ratio': sale_ratio,
    'review_ratio': review_ratio,
    'review_number': review_number,
    'thumbnail': thumbnail
})

# Index 컬럼 추가
product_info.insert(0, 'id', range(1, len(product_info) + 1))  # 1부터 시작하는 ID 추가

# CSV 파일로 저장
product_info.to_csv("product_info.csv", index=False, encoding='utf-8-sig')

#### 리뷰 데이터프레임을 위한 리스트 초기화####
review_product_id = []  # product_id
review_reviewer = []  # 리뷰 작성자
review_date = []  # 리뷰 날짜
review_text = []  # 리뷰 내용

## 리뷰 데이터 수집

# 위쪽에서 수집한 링크 리스트를 for문으로 순회해서 사용
for linklist in href_values:
    for link in linklist:
        driver.get("https://zigzag.kr/" + link)  # 상품 링크를 활용해각 각 상품 페이지로 이동
        time.sleep(2)  # 페이지 로드 대기
        print(link)

        ## 스크롤 및 리뷰 탭
        # 스크롤을 통해 페이지 로드
        for _ in range(5):  # (600 픽셀, 0.1초 대기) 스크롤 5번 반복
            driver.execute_script("window.scrollBy(0, 600);")  # 600픽셀씩 스크롤
            time.sleep(0.1)  # 0.1초 페이지 로드 대기

        # 현재 페이지의 HTML 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            # 리뷰 탭 버튼이 로드될 때까지 대기 후, 클릭
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-custom-ta-key="PDP_REVIEW_TAB_13"]'))
            )
            # 버튼 클릭
            button.click()
            time.sleep(2)  # 리뷰 탭 로드 대기
        except Exception as e:  # 예외 처리, 리뷰 버튼 클릭 중 문제가 발생했을 때 다음으로 넘어가도록 처리함
            print(f"An error occurred while clicking the button: {e}")
            continue  # 다음 링크로 넘어감

        # 더보기 클릭 시도 코드
        while True:
            try:
                # '더보기' 버튼이 화면에 나타날 때까지 최대 3초간 대기하고, 클릭 가능 상태 확인
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".BODY_13.BOLD.css-1aa4nqt.e1loaqv41"))
                )
                # '더보기' 버튼이 보이도록 화면을 해당 버튼 위치로 스크롤
                driver.execute_script("arguments[0].scrollIntoView();", button)
                driver.execute_script("arguments[0].click();", button)  # JavaScript를 이용해 '더보기' 버튼 클릭
                time.sleep(0.5)  # 클릭 후 로딩 시간을 고려하여 0.5초간 대기

            # '더보기' 버튼이 더 이상 존재하지 않은 경우 반복문 종료
            except:
                break

        # 리뷰 리스트를 찾기
        soup = BeautifulSoup(driver.page_source, "html.parser")  # 버튼 클릭 후 다시 HTML 파싱
        review_list = soup.find_all('div', {'data-review-feed-index': True})  # 리뷰 요소 찾기

        # 리뷰 데이터 수집
        for review in review_list:
            index = int(review['data-review-feed-index'])  # 인덱스 가져오기

            # 각 태그별 데이터를 찾음
            reviewer = review.find('span',class_='BODY_14 SEMIBOLD css-v0z0bg e1oql6860')  # span태그 중 동일한 class 값을 갖고 있는 첫번째 데이터를 변수에 저장함
            date = review.find('span',class_='BODY_17 REGULAR CAPTION_12 SEMIBOLD css-e9zz9 e1oql6860')  # span태그 중 동일한 class 값을 갖고 있는 첫번째 데이터를 변수에 저장함
            text = review.find('div',class_='BODY_14 REGULAR css-epr5m6 e1loaqv40')  ##div태그 중 동일한 class 값을 갖고 있는 첫번째 데이터를 변수에 저장함

            # 리뷰 데이터를 텍스트로 추출 후 review_product_id, review_reviewer, review_date, review_text 리스트에 추가함, 각 필드에 정보가 없다면 "N/A" 값으로 저장함.
            review_product_id.append(link)  # 제품 ID 추가
            review_reviewer.append(reviewer.get_text() if reviewer else "N/A")  # 리뷰어 이름 추가,미존재시 N/A로 출력
            review_date.append(date.get_text() if date else "N/A")  # 리뷰 날짜 추가,미존재시 N/A로 출력
            review_text.append(text.get_text() if text else "N/A")  # 리뷰 텍스트 추가,미존재시 N/A로 출력

# # 리뷰 데이터프레임 생성
product_review = pd.DataFrame({
    'product_id': review_product_id,
    'reviewer': review_reviewer,
    'date': review_date,
    'text': review_text
})
def extract_number(a): # 마지막 슬래시(/) 뒤에 나오는 부분만 추출하여 반환하는 함수 생성함
    return a.split('/')[-1]

# product_id컬럼에 extract_number 함수를 적용한 결과를 다시 저장함
product_review['product_id'] = product_review['product_id'].apply(extract_number)

# 데이터프레임의 첫 번째 열에 Index 컬럼을 추가하여 행 번호를 부여
product_review.insert(0, 'id', range(1, len(product_review) + 1))  # 1부터 시작하는 ID 추가, 행 번호 부여

# 리뷰 데이터프레임을 CSV로 저장
product_review.to_csv("product_review.csv", index=False, encoding='utf-8-sig')

# 드라이버 종료
driver.quit()