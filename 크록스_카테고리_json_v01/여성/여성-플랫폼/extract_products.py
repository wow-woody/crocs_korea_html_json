from bs4 import BeautifulSoup
import json
import re

# HTML 파일 읽기
with open('여성-플랫폼.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(html_content, 'html.parser')

products = []
product_number = 1

# .ok-card-list의 모든 li 요소 찾기
card_list = soup.find('ul', class_='ok-card-list')
if card_list:
    li_elements = card_list.find_all('li')
    
    for li in li_elements:
        # .ok-card가 있는 li만 처리 (빈 li는 제외)
        card = li.find('div', class_='ok-card')
        if not card:
            continue
        
        # 상품 ID 추출
        product_id = card.get('data-pidmaster', '')
        
        # 상품명 추출
        product_name_elem = card.find(class_='ok-card__product-name')
        product_name = product_name_elem.get_text(strip=True) if product_name_elem else ''
        
        # 색상 추출 (RGB 색상 배열)
        colors = []
        color_swatches = card.find_all(class_='ok-card__swatch-color')
        for swatch in color_swatches:
            style = swatch.get('style', '')
            if 'background:' in style and 'rgb(' in style:
                rgb_match = re.search(r'rgb\([^)]+\)', style)
                if rgb_match:
                    colors.append(rgb_match.group())
        
        # 가격 정보 추출
        price_section = card.find(class_='ok-card__price')
        price = ''
        sale_price = ''
        discount_range = ''
        sale_price_2 = ''
        original_price = ''
        
        if price_section:
            # 기본 가격 (할인가가 아닌 굵은 글씨 가격)
            price_elem = price_section.find(class_=['ok-card__price-value', 'ok-card__price-value--bold'])
            if price_elem and 'ok-card__price-value--sale' not in price_elem.get('class', []):
                price = price_elem.get_text(strip=True)
            
            # 할인가 (세일 가격)
            sale_elem = price_section.find(class_='ok-card__price-value--sale')
            if sale_elem:
                sale_price = sale_elem.get_text(strip=True)
            
            # 할인 범위 (~)
            price_to_elem = price_section.find(class_='ok-card__price-to')
            if price_to_elem:
                discount_range = price_to_elem.get_text(strip=True)
            
            # 할인 전 원가
            discounted_elem = price_section.find(class_='ok-card__price-value--discounted')
            if discounted_elem:
                original_price = discounted_elem.get_text(strip=True)
        
        # 리뷰수 추출
        review_elem = card.find(class_='ok-star-ratings__ratings-reviewcount')
        review_count = review_elem.get_text(strip=True) if review_elem else ''
        
        # 카테고리 추출
        category_elem = card.find(class_='ok-card__snipe')
        category = ''
        if category_elem:
            span_elem = category_elem.find('span')
            if span_elem:
                category = span_elem.get_text(strip=True)
        
        # 상품 이미지 추출
        images = []
        image_wrap = card.find(class_='ok-card__image-wrap')
        if image_wrap:
            img_elements = image_wrap.find_all('img')
            for img in img_elements:
                src = img.get('src')
                if src:
                    images.append(src)
        
        # 상품 정보가 유효한 경우에만 추가
        if product_id or product_name or images:
            product_data = {
                "번호": product_number,
                "상품 ID": product_id,
                "상품명": product_name,
                "색상": colors,
                "가격": price,
                "할인가 할인율": sale_price,
                "할인~": discount_range,
                "할인가-2": sale_price_2,
                "할인 전 원가": original_price,
                "별점 이미지": "./images/icon_start.svg",
                "리뷰수": review_count,
                "카테고리": category,
                "상품 이미지": images
            }
            products.append(product_data)
            product_number += 1

# JSON 파일로 저장
with open('여성-플랫폼.json', 'w', encoding='utf-8') as file:
    json.dump(products, file, ensure_ascii=False, indent=2)

print(f"총 {len(products)}개의 상품이 추출되었습니다.")
print("JSON 파일이 생성되었습니다: 여성-플랫폼.json")