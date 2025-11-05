import json
import re

def extract_rgb_colors(style_attr):
    """스타일 속성에서 RGB 색상 값을 추출"""
    if not style_attr:
        return []
    
    # rgb() 패턴 찾기
    rgb_pattern = r'rgb\((\d+),\s*(\d+),\s*(\d+)\)'
    matches = re.findall(rgb_pattern, style_attr)
    
    colors = []
    for match in matches:
        r, g, b = match
        colors.append(f"rgb({r}, {g}, {b})")
    
    return colors

def extract_text_between(text, start_tag, end_tag):
    """시작 태그와 끝 태그 사이의 텍스트 추출"""
    start_idx = text.find(start_tag)
    if start_idx == -1:
        return ""
    start_idx += len(start_tag)
    end_idx = text.find(end_tag, start_idx)
    if end_idx == -1:
        return ""
    return text[start_idx:end_idx].strip()

def extract_attribute_value(text, attr_name):
    """HTML 텍스트에서 속성 값 추출"""
    pattern = f'{attr_name}="([^"]*)"'
    match = re.search(pattern, text)
    return match.group(1) if match else ""

def clean_text(text):
    """텍스트 정리"""
    if not text:
        return ""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip().replace('\n', '').replace('\t', '').replace('  ', ' ')

def extract_products_from_html():
    """HTML 파일에서 상품 정보를 추출하여 JSON으로 저장"""
    
    # HTML 파일 읽기
    with open('신상품&트렌드.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # ok-card 패턴을 찾아서 상품 정보 추출
    card_pattern = r'<div class="ok-card"[^>]*data-pidmaster="([^"]*)"[^>]*>(.*?)</div>\s*</li>'
    card_matches = re.findall(card_pattern, content, re.DOTALL)
    
    products = []
    product_number = 1
    
    for match in card_matches:
        product_id = match[0]
        card_content = match[1]
        
        # 상품명 추출
        name_pattern = r'<div class="ok-card__product-name"[^>]*>(.*?)</div>'
        name_match = re.search(name_pattern, card_content, re.DOTALL)
        product_name = clean_text(name_match.group(1)) if name_match else ""
        
        # 색상 정보 추출
        colors = []
        color_pattern = r'<li class="ok-card__swatch-color"[^>]*style="([^"]*)"'
        color_matches = re.findall(color_pattern, card_content)
        for style_attr in color_matches:
            extracted_colors = extract_rgb_colors(style_attr)
            colors.extend(extracted_colors)
        
        # 가격 정보 추출
        regular_price = ""
        sale_price = ""
        original_price = ""
        
        # 일반 가격 (할인이 없는 경우)
        price_pattern = r'<span[^>]*class="[^"]*ok-card__price-value[^"]*ok-card__price-value--bold[^"]*"[^>]*>([^<]*)</span>'
        price_matches = re.findall(price_pattern, card_content)
        if price_matches:
            for price_text in price_matches:
                if '(' not in price_text:  # 할인율이 포함되지 않은 경우
                    regular_price = clean_text(price_text)
                    break
        
        # 할인가격과 할인율
        sale_pattern = r'<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]*)</span>'
        sale_match = re.search(sale_pattern, card_content)
        if sale_match:
            sale_price = clean_text(sale_match.group(1))
        
        # 할인 전 원가
        original_pattern = r'<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>.*?</span>([^<]*)</span>'
        original_match = re.search(original_pattern, card_content)
        if original_match:
            original_price = clean_text(original_match.group(1))
        
        # 별점 이미지 경로 설정
        star_image_path = "크록스 클래식_v02_2025-11-05(수)\\images\\icon_start.svg"
        
        # 리뷰수 추출
        review_count = ""
        review_pattern = r'<div class="ok-star-ratings__ratings-reviewcount"[^>]*>.*?\((\d+)\)'
        review_match = re.search(review_pattern, card_content, re.DOTALL)
        if review_match:
            review_count = review_match.group(1)
        
        # 카테고리 추출
        category = ""
        category_pattern = r'<div class="ok-card__snipe"[^>]*>.*?<span[^>]*>(.*?)</span>'
        category_match = re.search(category_pattern, card_content, re.DOTALL)
        if category_match:
            category = clean_text(category_match.group(1))
        
        # 상품 이미지 추출
        images = []
        image_pattern = r'<div class="ok-card__image-wrap"[^>]*>(.*?)</div>'
        image_wrap_match = re.search(image_pattern, card_content, re.DOTALL)
        if image_wrap_match:
            img_content = image_wrap_match.group(1)
            src_pattern = r'<img[^>]*src="([^"]*)"'
            src_matches = re.findall(src_pattern, img_content)
            images = src_matches
        
        # 상품 정보 딕셔너리 생성
        product = {
            "번호": product_number,
            "상품 ID": product_id,
            "상품명": product_name,
            "색상": colors,
            "가격": regular_price if regular_price else (sale_price.split('(')[0].strip() if sale_price else ""),
            "할인가 할인율": sale_price if sale_price else "",
            "할인 전 원가": original_price,
            "별점 이미지": star_image_path,
            "리뷰수": review_count,
            "카테고리": category,
            "상품 이미지": images
        }
        
        products.append(product)
        product_number += 1
        
        print(f"상품 {product_number-1} 처리 완료: {product_name}")
    
    # JSON 파일로 저장
    with open('크록스_상품목록.json', 'w', encoding='utf-8') as json_file:
        json.dump(products, json_file, ensure_ascii=False, indent=2)
    
    print(f"\n총 {len(products)}개의 상품을 추출하여 '크록스_상품목록.json' 파일로 저장했습니다.")
    
    # 첫 번째 상품 정보를 예시로 출력
    if products:
        print("\n첫 번째 상품 예시:")
        print(json.dumps(products[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    extract_products_from_html()