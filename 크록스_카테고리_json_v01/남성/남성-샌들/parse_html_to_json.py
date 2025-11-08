import json
import re
from bs4 import BeautifulSoup

def parse_html_to_json(html_file_path, output_file_path):
    # HTML 파일 읽기
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')
     
    # .ok-card-list 찾기
    card_list = soup.find('ul', class_='ok-card-list')
    if not card_list:
        print("ok-card-list를 찾을 수 없습니다.")
        return
    
    products = []
    product_number = 1
    
    # 각 li 요소 처리
    for li in card_list.find_all('li'):
        # .ok-card가 있는 li만 처리 (첫 번째 story-card 제외)
        ok_card = li.find('div', class_='ok-card')
        if not ok_card:
            continue
            
        product = {}
        
        # 번호
        product["번호"] = product_number
        
        # 상품 ID (data-pidmaster)
        product_id = ok_card.get('data-pidmaster', '')
        product["상품 ID"] = product_id
        
        # 상품명
        product_name_elem = ok_card.find(class_='ok-card__product-name')
        product_name = product_name_elem.get_text(strip=True) if product_name_elem else ''
        product["상품명"] = product_name
        
        # 색상 정보 추출
        colors = []
        swatches_list = ok_card.find('ul', class_='ok-card__swatches--list')
        if swatches_list:
            for swatch in swatches_list.find_all('li', class_='ok-card__swatch-color'):
                style = swatch.get('style', '')
                if 'background:' in style:
                    colors.append(style)
        product["색상"] = colors
        
        # 가격 정보 추출
        price_section = ok_card.find('div', class_='ok-card__price')
        if price_section:
            # 할인가 할인율 (세일 가격)
            sale_price_elem = price_section.find(class_='ok-card__price-value--sale')
            sale_price = ''
            if sale_price_elem:
                sale_price = sale_price_elem.get_text(strip=True)
                # 불필요한 텍스트 제거 (;undefined 등)
                sale_price = re.sub(r';undefined', '', sale_price)
            
            product["가격"] = sale_price
            product["할인가 할인율"] = sale_price
            
            # 할인~ (가격 범위 표시)
            price_to_elem = price_section.find(class_='ok-card__price-to')
            price_to = price_to_elem.get_text(strip=True) if price_to_elem else ''
            product["할인~"] = price_to
            
            # 할인가-2 (일반 가격 - 할인되지 않은 가격)
            regular_price_elems = price_section.find_all('span', class_='ok-card__price-value')
            regular_price = ''
            for elem in regular_price_elems:
                elem_classes = elem.get('class', [])
                if ('ok-card__price-value--bold' in elem_classes and 
                    'ok-card__price-value--sale' not in elem_classes and 
                    'ok-card__price-value--discounted' not in elem_classes):
                    regular_price = elem.get_text(strip=True)
                    break
            product["할인가-2"] = regular_price
            
            # 할인 전 원가
            discounted_price_elem = price_section.find(class_='ok-card__price-value--discounted')
            discounted_price = ''
            if discounted_price_elem:
                discounted_price = discounted_price_elem.get_text(strip=True)
                # 불필요한 텍스트 제거
                discounted_price = re.sub(r';undefined', '', discounted_price)
            product["할인 전 원가"] = discounted_price
        else:
            product["가격"] = ''
            product["할인가 할인율"] = ''
            product["할인~"] = ''
            product["할인가-2"] = ''
            product["할인 전 원가"] = ''
        
        # 별점 이미지 (고정값)
        product["별점 이미지"] = "./images/icon_start.svg"
        
        # 리뷰수
        review_count_elem = ok_card.find(class_='ok-star-ratings__ratings-reviewcount')
        review_count = ''
        if review_count_elem:
            review_text = review_count_elem.get_text(strip=True)
            # 괄호 안의 숫자만 추출
            match = re.search(r'\((\d+)\)', review_text)
            if match:
                review_count = match.group(1)
        product["리뷰수"] = review_count
        
        # 카테고리
        category_elem = ok_card.find(class_='ok-card__snipe')
        category = ''
        if category_elem:
            span_elem = category_elem.find('span')
            if span_elem:
                category = span_elem.get_text(strip=True)
        product["카테고리"] = category
        
        # 상품 이미지
        image_wrap = ok_card.find(class_='ok-card__image-wrap')
        images = []
        if image_wrap:
            for img in image_wrap.find_all('img'):
                src = img.get('src', '')
                if src:
                    images.append(src)
        product["상품 이미지"] = images
        
        products.append(product)
        product_number += 1
    
    # JSON 파일로 저장
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(products, json_file, ensure_ascii=False, indent=4)
    
    print(f"JSON 파일이 생성되었습니다: {output_file_path}")
    print(f"총 {len(products)}개의 상품이 처리되었습니다.")

if __name__ == "__main__":
    html_file = "남성-샌들.html"
    json_file = "남성-샌들.json"
    
    parse_html_to_json(html_file, json_file)