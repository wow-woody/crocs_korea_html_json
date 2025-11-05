import re
import json

# HTML 파일 읽기
with open('여성-플랫폼.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

products = []

# 각 li 태그와 그 안의 ok-card를 찾기
li_pattern = r'<li[^>]*>.*?</li>'
li_matches = re.finditer(li_pattern, html_content, re.DOTALL)

product_number = 1

for li_match in li_matches:
    li_content = li_match.group()
    
    # ok-card가 있는지 확인
    if 'class="ok-card"' not in li_content:
        continue
    
    # 상품 ID 추출
    product_id_match = re.search(r'data-pidmaster="([^"]*)"', li_content)
    product_id = product_id_match.group(1) if product_id_match else ''
    
    if not product_id:
        continue
    
    # aria-label에서 상품명 추출
    aria_label_match = re.search(r'aria-label="([^"]*)"', li_content)
    product_name = aria_label_match.group(1) if aria_label_match else ''
    
    # ok-card__product-name에서도 상품명 추출 시도
    if not product_name:
        product_name_match = re.search(r'<div class="ok-card__product-name"[^>]*>([^<]*)</div>', li_content)
        product_name = product_name_match.group(1).strip() if product_name_match else ''
    
    # 색상 추출
    colors = []
    color_matches = re.findall(r'<li class="ok-card__swatch-color"[^>]*style="background:\s*([^"]*)"', li_content)
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
    
    # 할인가 (sale price)
    sale_price_match = re.search(r'<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]*)</span>', li_content)
    if sale_price_match:
        sale_price = sale_price_match.group(1).strip()
    
    # 일반 가격 (할인가가 없는 경우)
    if not sale_price:
        price_match = re.search(r'<span[^>]*class="[^"]*ok-card__price-value[^"]*ok-card__price-value--bold[^"]*"[^>]*>([^<]*)</span>', li_content)
        if price_match:
            price = price_match.group(1).strip()
    
    # 할인 범위
    discount_range_match = re.search(r'<span class="ok-card__price-to"[^>]*>([^<]*)</span>', li_content)
    if discount_range_match:
        discount_range = discount_range_match.group(1).strip()
    
    # 할인가-2 (범위의 끝 가격)
    price_2_match = re.search(r'<span class="ok-card__price-to"[^>]*>[^<]*</span>([^<]*)</span>', li_content)
    price_2 = price_2_match.group(1).strip() if price_2_match else ''
    
    # 할인 전 원가
    original_price_match = re.search(r'<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>([^<]*)</span>', li_content)
    if original_price_match:
        original_price = original_price_match.group(1).strip()
    
    # 리뷰수 추출
    review_match = re.search(r'<div class="ok-star-ratings__ratings-reviewcount"[^>]*>([^<]*)</div>', li_content)
    review_count = review_match.group(1).strip() if review_match else ''
    
    # 카테고리 추출
    category_match = re.search(r'<div class="ok-card__snipe"[^>]*><span[^>]*>([^<]*)</span>', li_content)
    category = category_match.group(1).strip() if category_match else ''
    
    # 상품 이미지 추출
    images = []
    img_matches = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', li_content)
    for img in img_matches:
        if img and img.startswith('http'):
            images.append(img)
    
    # 상품 정보 추가
    product_data = {
        "번호": product_number,
        "상품 ID": product_id,
        "상품명": product_name,
        "색상": colors,
        "가격": price,
        "할인가 할인율": sale_price,
        "할인~": discount_range,
        "할인가-2": price_2,
        "할인 전 원가": original_price,
        "별점 이미지": "./images/icon_start.svg",
        "리뷰수": review_count,
        "카테고리": category,
        "상품 이미지": images
    }
    products.append(product_data)
    product_number += 1

# JSON 파일로 저장
with open('여성-플랫폼_완전판.json', 'w', encoding='utf-8') as file:
    json.dump(products, file, ensure_ascii=False, indent=2)

print(f"총 {len(products)}개의 상품이 추출되었습니다.")

# 처음 5개 상품 미리보기
print("\n처음 5개 상품:")
for i in range(min(5, len(products))):
    print(f"{i+1}. {products[i]['상품명']} (ID: {products[i]['상품 ID']})")
    print(f"   가격: {products[i]['가격']} / 할인가: {products[i]['할인가 할인율']}")
    print(f"   색상 수: {len(products[i]['색상'])}")
    print(f"   이미지 수: {len(products[i]['상품 이미지'])}")
    print()