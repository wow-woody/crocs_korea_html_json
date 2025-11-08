#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from bs4 import BeautifulSoup

def extract_rgb_colors(style_attr):
    """스타일 속성에서 RGB 색상을 추출"""
    if not style_attr:
        return ""
    
    # RGB 패턴 찾기
    rgb_pattern = r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
    matches = re.findall(rgb_pattern, style_attr)
    
    if matches:
        colors = []
        for match in matches:
            r, g, b = match
            colors.append(f"rgb({r}, {g}, {b})")
        return ", ".join(colors)
    return ""

def clean_text(text):
    """텍스트에서 불필요한 공백과 문자를 제거"""
    if not text:
        return ""
    # 여러 공백을 하나로, 줄바꿈 제거, 앞뒤 공백 제거
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def clean_price_text(text):
    """가격 텍스트에서 불필요한 문자 제거"""
    if not text:
        return ""
    # ;undefined 제거하고 텍스트 정리
    cleaned = text.replace(';undefined', '').strip()
    return clean_text(cleaned)

def extract_products_from_html(html_file_path):
    """HTML 파일에서 상품 정보를 추출하여 리스트로 반환"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # .ok-card-list 찾기
        card_list = soup.find('ul', class_='ok-card-list')
        if not card_list:
            print("Error: .ok-card-list를 찾을 수 없습니다.")
            return []
        
        # 모든 li 요소 가져오기 (빈 li 제외)
        list_items = card_list.find_all('li')
        products = []
        product_number = 1
        
        for li in list_items:
            # .ok-card가 있는 li만 처리
            card = li.find('div', class_='ok-card')
            if not card:
                continue
            
            # 상품 ID (data-pidmaster)
            product_id = card.get('data-pidmaster', '')
            
            # 상품명
            product_name_elem = card.find(class_='ok-card__product-name')
            product_name = product_name_elem.get_text(strip=True) if product_name_elem else ''
            
            # 색상 정보
            colors = []
            swatch_colors = card.find_all(class_='ok-card__swatch-color')
            for swatch in swatch_colors:
                style = swatch.get('style', '')
                color = extract_rgb_colors(style)
                if color:
                    colors.append(color)
            
            # 가격 정보 - 기본 가격 (할인가가 아닌)
            price_elem = card.find(class_='ok-card__price-value--bold')
            if price_elem and 'ok-card__price-value--sale' not in price_elem.get('class', []):
                price = clean_text(price_elem.get_text(strip=True))
            else:
                price = ''
            
            # 할인가 할인율
            sale_price_elem = card.find(class_='ok-card__price-value--sale')
            sale_price = clean_text(sale_price_elem.get_text(strip=True)) if sale_price_elem else ''
            
            # 할인~ (가격 범위)
            price_to_elem = card.find(class_='ok-card__price-to')
            price_to = clean_text(price_to_elem.get_text(strip=True)) if price_to_elem else ''
            
            # 할인가-2 (가격 범위의 두 번째 가격)
            price_2 = ''
            if price_to:  # 가격 범위가 있는 경우
                price_range_elems = card.find_all(class_='ok-card__price-value--sale')
                for elem in price_range_elems:
                    text = clean_text(elem.get_text(strip=True))
                    if price_to in text and text != sale_price:
                        # ~ 다음의 가격 추출
                        parts = text.split(price_to)
                        if len(parts) > 1:
                            price_2 = clean_text(parts[1])
                        break
            
            # 할인 전 원가
            discounted_price_elem = card.find(class_='ok-card__price-value--discounted')
            original_price = clean_price_text(discounted_price_elem.get_text(strip=True)) if discounted_price_elem else ''
            
            # 리뷰수
            review_count_elem = card.find(class_='ok-star-ratings__ratings-reviewcount')
            review_count = clean_text(review_count_elem.get_text(strip=True)) if review_count_elem else ''
            
            # 카테고리
            snipe_elem = card.find(class_='ok-card__snipe')
            category = ''
            if snipe_elem:
                span_elem = snipe_elem.find('span')
                category = span_elem.get_text(strip=True) if span_elem else ''
            
            # 상품 이미지
            image_wrap = card.find(class_='ok-card__image-wrap')
            images = []
            if image_wrap:
                img_elems = image_wrap.find_all('img')
                for img in img_elems:
                    src = img.get('src', '')
                    if src:
                        images.append(src)
            
            # 상품 정보 딕셔너리 생성
            product = {
                "번호": product_number,
                "상품 ID": product_id,
                "상품명": product_name,
                "색상": ", ".join(colors) if colors else "",
                "가격": price,
                "할인가 할인율": sale_price,
                "할인~": price_to,
                "할인가-2": price_2,
                "할인 전 원가": original_price,
                "별점 이미지": "./images/icon_start.svg",
                "리뷰수": review_count,
                "카테고리": category,
                "상품 이미지": images
            }
            
            products.append(product)
            product_number += 1
        
        return products
        
    except FileNotFoundError:
        print(f"Error: '{html_file_path}' 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"Error: HTML 파싱 중 오류가 발생했습니다: {str(e)}")
        return []

def main():
    html_file = "여성-플랫_스니커즈_로퍼.html"
    json_file = "여성-플랫_스니커즈_로퍼.json"
    
    print("HTML 파일에서 상품 정보를 추출하는 중...")
    products = extract_products_from_html(html_file)
    
    if products:
        # JSON 파일로 저장
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 성공적으로 {len(products)}개의 상품 정보를 '{json_file}' 파일로 저장했습니다.")
            
            # 첫 번째 상품 정보 미리보기
            if products:
                print("\n📋 첫 번째 상품 정보 미리보기:")
                print(json.dumps(products[0], ensure_ascii=False, indent=2))
                
        except Exception as e:
            print(f"❌ JSON 파일 저장 중 오류가 발생했습니다: {str(e)}")
    else:
        print("❌ 추출된 상품 정보가 없습니다.")

if __name__ == "__main__":
    main()