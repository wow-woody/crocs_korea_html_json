import re
import json
from bs4 import BeautifulSoup

# HTML 파일 읽기
with open('여성-클로그_1.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 상품 카드들을 찾기
product_cards = soup.select('.ok-card[data-pidmaster]')

products = []

for index, card in enumerate(product_cards, 1):
    try:
        # 상품 ID
        product_id = card.get('data-pidmaster', '')
        
        # 상품명
        product_name = ''
        name_elem = card.select_one('.ok-card__product-name')
        if name_elem:
            product_name = name_elem.get_text(strip=True)
        
        # 색상 정보 (color swatches에서 RGB 값 추출)
        colors = []
        color_elems = card.select('.ok-card__swatch-color')
        for color_elem in color_elems:
            style = color_elem.get('style', '')
            if 'background:' in style:
                # RGB 값이나 색상 정보 추출
                if 'rgb(' in style:
                    rgb_matches = re.findall(r'rgb\((\d+, \d+, \d+)\)', style)
                    for rgb in rgb_matches:
                        colors.append(f'rgb({rgb})')
                elif 'linear-gradient' in style:
                    colors.append('그라데이션')
        
        if not colors:
            colors = ['색상정보없음']
        
        # 가격 정보
        price_info = {}
        price_container = card.select_one('.ok-card__price')
        
        if price_container:
            # 할인가
            sale_price_elem = price_container.select_one('.ok-card__price-value--sale')
            if sale_price_elem:
                sale_text = sale_price_elem.get_text(strip=True)
                price_info['할인가'] = sale_text
                
                # 할인율 추출
                if '(' in sale_text and '%' in sale_text:
                    discount_match = re.search(r'\((\d+%)\)', sale_text)
                    if discount_match:
                        price_info['할인율'] = discount_match.group(1)
                        price_info['할인가-2'] = sale_text.split('(')[0].strip()
            
            # 원가
            original_price_elem = price_container.select_one('.ok-card__price-value--discounted')
            if original_price_elem:
                price_info['할인 전 원가'] = original_price_elem.get_text(strip=True)
            
            # 일반 가격 (할인이 없는 경우)
            regular_price_elem = price_container.select_one('.ok-card__price-value--bold:not(.ok-card__price-value--sale)')
            if regular_price_elem and not price_info.get('할인가'):
                price_info['가격'] = regular_price_elem.get_text(strip=True)
            
            # 가격 범위 처리
            price_range_elem = price_container.select_one('.ok-card__price-to')
            if price_range_elem:
                parent_text = price_range_elem.parent.get_text(strip=True) if price_range_elem.parent else ''
                if '~' in parent_text:
                    price_info['할인~'] = parent_text
        
        # 별점 및 리뷰수
        rating_info = {}
        rating_elem = card.select_one('.ok-star-ratings__ratings-stars-average')
        if rating_elem:
            width = rating_elem.get('style', '')
            if 'width:' in width:
                width_value = re.search(r'width:\s*(\d+)%', width)
                if width_value:
                    rating_percent = int(width_value.group(1))
                    rating_info['별점'] = f'{rating_percent/20:.1f}'
        
        review_elem = card.select_one('.ok-star-ratings__ratings-reviewcount')
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            review_match = re.search(r'\((\d+)\)', review_text)
            if review_match:
                rating_info['리뷰수'] = review_match.group(1)
        
        # 상품 이미지
        img_elem = card.select_one('.ok-card__image-wrap img')
        image_url = ''
        if img_elem:
            image_url = img_elem.get('src', '')
        
        # 카테고리 (기본값)
        category = '여성-클로그'
        
        # 상품 데이터 구성
        product = {
            '번호': index,
            '상품 ID': product_id,
            '상품명': product_name,
            '색상': colors[:5] if len(colors) > 5 else colors,  # 최대 5개 색상만
            '가격': price_info.get('가격', ''),
            '할인가 할인율': price_info.get('할인가', ''),
            '할인~': price_info.get('할인~', ''),
            '할인가-2': price_info.get('할인가-2', ''),
            '할인 전 원가': price_info.get('할인 전 원가', ''),
            '별점 이미지': rating_info.get('별점', ''),
            '리뷰수': rating_info.get('리뷰수', ''),
            '카테고리': category,
            '상품 이미지': image_url
        }
        
        products.append(product)
        
    except Exception as e:
        print(f'상품 {index} 처리 중 오류: {e}')
        continue

# JSON 파일로 저장
with open('여성-클로그.json', 'w', encoding='utf-8') as json_file:
    json.dump(products, json_file, ensure_ascii=False, indent=2)

print(f'총 {len(products)}개의 상품이 추출되어 여성-클로그.json 파일에 저장되었습니다.')

# 처음 3개 상품 미리보기
for i in range(min(3, len(products))):
    print(f'\n상품 {i+1}: {products[i]["상품명"]}')
    print(f'  - 상품 ID: {products[i]["상품 ID"]}')
    print(f'  - 색상: {products[i]["색상"][:2]}...')
    print(f'  - 가격정보: {products[i]["할인가 할인율"]}')