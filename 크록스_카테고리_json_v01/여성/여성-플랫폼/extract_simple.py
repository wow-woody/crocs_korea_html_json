import json
import re

# HTML 파일 읽기
with open('여성-플랫폼.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

products = []
product_number = 1

# 각 ok-card div 찾기
card_pattern = r'<div class="ok-card"[^>]*data-pidmaster="([^"]*)"[^>]*>.*?</div>\s*</div>\s*</li>'
card_matches = re.findall(card_pattern, html_content, re.DOTALL)

# 더 정확한 패턴으로 카드 분리
card_sections = re.split(r'<li[^>]*>\s*<div class="ok-card"', html_content)

for i, section in enumerate(card_sections[1:]):  # 첫 번째는 비어있으므로 제외
    try:
        # 상품 ID 추출
        product_id_match = re.search(r'data-pidmaster="([^"]*)"', section)
        product_id = product_id_match.group(1) if product_id_match else ''
        
        # 상품명 추출
        product_name_match = re.search(r'<div class="ok-card__product-name"[^>]*>([^<]*)</div>', section)
        product_name = product_name_match.group(1).strip() if product_name_match else ''
        
        # 색상 추출
        colors = []
        color_matches = re.findall(r'<li class="ok-card__swatch-color"[^>]*style="background:\s*([^"]*)"', section)
        for color in color_matches:
            if 'rgb(' in color:
                rgb_match = re.search(r'rgb\([^)]+\)', color)
                if rgb_match:
                    colors.append(rgb_match.group())
        
        # 가격 정보 추출
        price = ''
        sale_price = ''
        discount_range = ''
        original_price = ''
        
        # 기본 가격 (할인가가 아닌 경우)
        price_matches = re.findall(r'<span class="ok-card__price-value[^"]*ok-card__price-value--bold[^"]*"[^>]*>([^<]*)</span>', section)
        if price_matches:
            for p in price_matches:
                if 'ok-card__price-value--sale' not in section[section.find(p)-100:section.find(p)+100]:
                    price = p.strip()
                    break
        
        # 할인가
        sale_price_match = re.search(r'<span class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]*)</span>', section)
        if sale_price_match:
            sale_price = sale_price_match.group(1).strip()
        
        # 할인 범위
        discount_range_match = re.search(r'<span class="ok-card__price-to"[^>]*>([^<]*)</span>', section)
        if discount_range_match:
            discount_range = discount_range_match.group(1).strip()
        
        # 할인 전 원가
        original_price_match = re.search(r'<span class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>([^<]*)</span>', section)
        if original_price_match:
            original_price = original_price_match.group(1).strip()
        
        # 리뷰수 추출
        review_match = re.search(r'<div class="ok-star-ratings__ratings-reviewcount"[^>]*>([^<]*)</div>', section)
        review_count = review_match.group(1).strip() if review_match else ''
        
        # 카테고리 추출
        category_match = re.search(r'<div class="ok-card__snipe"[^>]*><span[^>]*>([^<]*)</span>', section)
        category = category_match.group(1).strip() if category_match else ''
        
        # 상품 이미지 추출
        images = []
        img_matches = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', section)
        for img in img_matches:
            if img and img.startswith('http'):
                images.append(img)
        
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
                "할인가-2": "",
                "할인 전 원가": original_price,
                "별점 이미지": "./images/icon_start.svg",
                "리뷰수": review_count,
                "카테고리": category,
                "상품 이미지": images
            }
            products.append(product_data)
            product_number += 1
            
    except Exception as e:
        print(f"상품 {i+1} 처리 중 오류: {e}")
        continue

# JSON 파일로 저장
with open('여성-플랫폼.json', 'w', encoding='utf-8') as file:
    json.dump(products, file, ensure_ascii=False, indent=2)

print(f"총 {len(products)}개의 상품이 추출되었습니다.")
print("JSON 파일이 생성되었습니다: 여성-플랫폼.json")

# 처음 3개 상품 미리보기
if products:
    print("\n처음 3개 상품 미리보기:")
    for i in range(min(3, len(products))):
        print(f"\n상품 {i+1}:")
        for key, value in products[i].items():
            print(f"  {key}: {value}")