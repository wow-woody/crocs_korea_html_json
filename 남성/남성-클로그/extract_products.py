import json
import re
from bs4 import BeautifulSoup

def extract_product_data(html_file_path):
    """HTML 파일에서 상품 데이터를 추출하여 JSON 형태로 반환"""
    
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ok-card 요소들을 찾기
    product_cards = soup.find_all('div', class_='ok-card')
    
    products = []
    
    for idx, card in enumerate(product_cards, 1):
        product_data = {
            "번호": idx,
            "상품 ID": "",
            "상품명": "",
            "색상": [],
            "가격": "",
            "할인가 할인율": "",
            "할인~": "",
            "할인가-2": "",
            "할인 전 원가": "",
            "별점 이미지": "./images/icon_start.svg",
            "리뷰수": "",
            "카테고리": "",
            "상품 이미지": []
        }
        
        # 상품 ID (data-pidmaster)
        pid_master = card.get('data-pidmaster')
        if pid_master:
            product_data["상품 ID"] = pid_master
        
        # 상품명
        product_name_elem = card.find('div', class_='ok-card__product-name')
        if product_name_elem:
            product_data["상품명"] = product_name_elem.get_text(strip=True)
        
        # 색상 정보 (ok-card__swatch-color의 style 속성에서 색상 추출)
        color_swatches = card.find_all('li', class_='ok-card__swatch-color')
        colors = []
        for swatch in color_swatches:
            style = swatch.get('style', '')
            if 'background:' in style:
                # RGB 값 추출
                rgb_match = re.search(r'rgb\(([^)]+)\)', style)
                if rgb_match:
                    colors.append(rgb_match.group(1))
        product_data["색상"] = colors
        
        # 가격 정보 처리
        price_section = card.find('div', class_='ok-card__price')
        if price_section:
            # 할인가 (ok-card__price-value--sale)
            sale_price_elem = price_section.find('span', class_='ok-card__price-value--sale')
            if sale_price_elem:
                sale_text = sale_price_elem.get_text(strip=True)
                # 할인율이 포함된 경우와 그렇지 않은 경우 구분
                if '(' in sale_text and ')' in sale_text:
                    product_data["할인가 할인율"] = sale_text
                else:
                    product_data["할인가 할인율"] = sale_text
            
            # 가격 범위 (~)
            price_to_elem = price_section.find('span', class_='ok-card__price-to')
            if price_to_elem:
                product_data["할인~"] = price_to_elem.get_text(strip=True)
            
            # 일반 가격
            price_values = price_section.find_all('span', class_='ok-card__price-value')
            for price_elem in price_values:
                if 'ok-card__price-value--sale' not in price_elem.get('class', []) and \
                   'ok-card__price-value--discounted' not in price_elem.get('class', []):
                    price_text = price_elem.get_text(strip=True)
                    if price_text and not price_text.startswith('~'):
                        product_data["할인가-2"] = price_text
            
            # 할인 전 원가
            original_price_elem = price_section.find('span', class_='ok-card__price-value--discounted')
            if original_price_elem:
                product_data["할인 전 원가"] = original_price_elem.get_text(strip=True)
            
            # 가격이 할인가가 없고 일반 가격만 있는 경우
            if not product_data["할인가 할인율"]:
                bold_price_elem = price_section.find('span', class_='ok-card__price-value--bold')
                if bold_price_elem:
                    product_data["가격"] = bold_price_elem.get_text(strip=True)
        
        # 리뷰수
        review_count_elem = card.find('div', class_='ok-star-ratings__ratings-reviewcount')
        if review_count_elem:
            review_text = review_count_elem.get_text(strip=True)
            # 괄호 안의 숫자만 추출
            review_match = re.search(r'\((\d+)\)', review_text)
            if review_match:
                product_data["리뷰수"] = review_match.group(1)
        
        # 카테고리 (ok-card__snipe > span)
        snipe_elem = card.find('div', class_='ok-card__snipe')
        if snipe_elem:
            span_elem = snipe_elem.find('span')
            if span_elem:
                category_text = span_elem.get_text(strip=True)
                if category_text:
                    product_data["카테고리"] = category_text
        
        # 상품 이미지
        image_wrap = card.find('div', class_='ok-card__image-wrap')
        if image_wrap:
            images = image_wrap.find_all('img')
            image_urls = []
            for img in images:
                src = img.get('src')
                if src:
                    image_urls.append(src)
            product_data["상품 이미지"] = image_urls
        
        products.append(product_data)
    
    return products

# 실행
if __name__ == "__main__":
    html_file = "남성-클로그.html"
    output_file = "남성-클로그.json"
    
    print("HTML 파일에서 상품 데이터 추출 중...")
    products = extract_product_data(html_file)
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(products)}개의 상품 데이터가 '{output_file}' 파일로 저장되었습니다.")
    
    # 처음 3개 상품 정보 미리보기
    print("\n=== 처음 3개 상품 미리보기 ===")
    for i, product in enumerate(products[:3]):
        print(f"\n상품 {i+1}:")
        print(f"  상품 ID: {product['상품 ID']}")
        print(f"  상품명: {product['상품명']}")
        print(f"  색상 수: {len(product['색상'])}개")
        print(f"  가격: {product['가격']}")
        print(f"  할인가: {product['할인가 할인율']}")
        print(f"  리뷰수: {product['리뷰수']}")
        print(f"  카테고리: {product['카테고리']}")
        print(f"  이미지 수: {len(product['상품 이미지'])}개")