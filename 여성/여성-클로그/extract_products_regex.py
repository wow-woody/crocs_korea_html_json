import re
import json

# HTML 파일 읽기
with open('여성-클로그_1.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# 상품 카드 패턴 찾기
product_pattern = r'<div class="ok-card"[^>]*data-pidmaster="([^"]+)"[^>]*>(.*?)</div>\s*(?=<div class="ok-card__promo"|<li|$)'

products = []
product_matches = re.findall(product_pattern, html_content, re.DOTALL)

print(f"찾은 상품 수: {len(product_matches)}")

for index, (product_id, card_content) in enumerate(product_matches, 1):
    try:
        # 상품명 추출
        name_pattern = r'<div class="ok-card__product-name"[^>]*>([^<]+)</div>'
        name_match = re.search(name_pattern, card_content)
        product_name = name_match.group(1).strip() if name_match else ''
        
        # 색상 정보 추출 (RGB 값)
        colors = []
        color_pattern = r'style="background:\s*([^"]+)"'
        color_matches = re.findall(color_pattern, card_content)
        
        for color_style in color_matches:
            if 'rgb(' in color_style:
                rgb_matches = re.findall(r'rgb\((\d+,\s*\d+,\s*\d+)\)', color_style)
                for rgb in rgb_matches:
                    colors.append(f'rgb({rgb})')
            elif 'linear-gradient' in color_style:
                colors.append('그라데이션')
        
        if not colors:
            colors = ['색상정보없음']
        
        # 가격 정보 추출
        price_info = {}
        
        # 할인가 추출
        sale_price_pattern = r'<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]+)</span>'
        sale_price_match = re.search(sale_price_pattern, card_content)
        if sale_price_match:
            sale_text = sale_price_match.group(1).strip()
            price_info['할인가'] = sale_text
            
            # 할인율 추출
            if '(' in sale_text and '%' in sale_text:
                discount_match = re.search(r'\((\d+%)\)', sale_text)
                if discount_match:
                    price_info['할인율'] = discount_match.group(1)
                    price_info['할인가-2'] = sale_text.split('(')[0].strip()
        
        # 원가 추출
        original_price_pattern = r'<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>(?:[^<]+)?([₩][^<]+)</span>'
        original_price_match = re.search(original_price_pattern, card_content)
        if original_price_match:
            price_info['할인 전 원가'] = original_price_match.group(1).strip()
        
        # 일반 가격 (할인이 없는 경우)
        regular_price_pattern = r'<span[^>]*class="[^"]*ok-card__price-value--bold[^"]*"[^>]*>([₩][^<]+)</span>'
        regular_price_match = re.search(regular_price_pattern, card_content)
        if regular_price_match and not price_info.get('할인가'):
            price_info['가격'] = regular_price_match.group(1).strip()
        
        # 가격 범위 처리
        price_range_pattern = r'<span class="ok-card__price-to">[^<]*~[^<]*</span>([₩][^<]+)</span>'
        price_range_match = re.search(price_range_pattern, card_content)
        if price_range_match:
            price_info['할인~'] = price_range_match.group(1).strip()
        
        # 별점 추출
        rating_info = {}
        rating_pattern = r'style="width:\s*(\d+)%"[^>]*><span[^>]*>([^<]+) out of 5 stars'
        rating_match = re.search(rating_pattern, card_content)
        if rating_match:
            width_percent = int(rating_match.group(1))
            rating_info['별점'] = f'{width_percent/20:.1f}'
        
        # 리뷰수 추출
        review_pattern = r'<div class="ok-star-ratings__ratings-reviewcount">[^(]*\((\d+)\)'
        review_match = re.search(review_pattern, card_content)
        if review_match:
            rating_info['리뷰수'] = review_match.group(1)
        
        # 상품 이미지 URL 추출
        image_pattern = r'<img[^>]*src="([^"]+)"[^>]*>'
        image_match = re.search(image_pattern, card_content)
        image_url = image_match.group(1) if image_match else ''
        
        # 카테고리
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
    print(f'  - 색상: {products[i]["색상"][:2] if len(products[i]["색상"]) > 2 else products[i]["색상"]}')
    print(f'  - 가격정보: {products[i]["할인가 할인율"] or products[i]["가격"]}')