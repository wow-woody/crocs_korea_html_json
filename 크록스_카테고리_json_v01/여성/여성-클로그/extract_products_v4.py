#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json
import re
import os

def extract_rgb_color(style_text):
    """style 속성에서 RGB 값을 추출"""
    if not style_text:
        return ""
    
    # rgb(숫자, 숫자, 숫자) 패턴 찾기
    rgb_match = re.search(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', style_text)
    if rgb_match:
        return f"rgb({rgb_match.group(1)}, {rgb_match.group(2)}, {rgb_match.group(3)})"
    return ""

def extract_products_from_html(html_file_path):
    """HTML 파일에서 상품 정보를 추출하여 JSON 형식으로 반환"""
    
    # HTML 파일 읽기
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # .ok-card-list 내의 모든 li 요소 찾기
    card_list = soup.find('ul', class_='ok-card-list')
    if not card_list:
        print("ok-card-list를 찾을 수 없습니다.")
        return []
    
    li_elements = card_list.find_all('li')
    products = []
    
    # 번호는 69부터 시작
    counter = 69
    
    for li in li_elements:
        # .ok-card가 있는 li만 처리
        card_div = li.find('div', class_='ok-card')
        if not card_div:
            continue
            
        product = {}
        
        # 번호
        product["번호"] = counter
        counter += 1
        
        # 상품 ID (data-pidmaster 속성)
        product_id = card_div.get('data-pidmaster', '')
        product["상품 ID"] = product_id
        
        # 상품명 (.ok-card__product-name)
        product_name_elem = card_div.find('div', class_='ok-card__product-name')
        product_name = product_name_elem.get_text(strip=True) if product_name_elem else ''
        product["상품명"] = product_name
        
        # 색상 (.ok-card__swatches--list 내의 .ok-card__swatch-color의 style 속성)
        colors = []
        swatches_list = card_div.find('div', class_='ok-card__swatches--list')
        if swatches_list:
            swatch_colors = swatches_list.find_all('div', class_='ok-card__swatch-color')
            for swatch in swatch_colors:
                style = swatch.get('style', '')
                rgb_color = extract_rgb_color(style)
                if rgb_color:
                    colors.append(rgb_color)
        product["색상"] = colors
        
        # 가격 정보들
        price_section = card_div.find('div', class_='ok-card__price')
        
        # 가격 (.ok-card__price-value ok-card__price-value--bold)
        price_bold = ""
        if price_section:
            price_bold_elem = price_section.find('span', class_=['ok-card__price-value', 'ok-card__price-value--bold'])
            if price_bold_elem and 'ok-card__price-value--sale' not in price_bold_elem.get('class', []):
                price_bold = price_bold_elem.get_text(strip=True)
        product["가격"] = price_bold
        
        # 할인가 할인율 (.ok-card__price-value--sale)
        sale_price = ""
        if price_section:
            sale_price_elem = price_section.find('span', class_='ok-card__price-value--sale')
            if sale_price_elem:
                sale_price = sale_price_elem.get_text(strip=True)
        product["할인가 할인율"] = sale_price
        
        # 할인~ (.ok-card__price-to)
        price_to = ""
        if price_section:
            price_to_elem = price_section.find(class_='ok-card__price-to')
            if price_to_elem:
                price_to = price_to_elem.get_text(strip=True)
        product["할인~"] = price_to
        
        # 할인가-2 (.ok-card__price-value 가격 텍스트) - sale이 아닌 일반 price-value
        price_value = ""
        if price_section:
            price_values = price_section.find_all('span', class_='ok-card__price-value')
            for pv in price_values:
                if 'ok-card__price-value--bold' not in pv.get('class', []) and 'ok-card__price-value--sale' not in pv.get('class', []) and 'ok-card__price-value--discounted' not in pv.get('class', []):
                    price_value = pv.get_text(strip=True)
                    break
        product["할인가-2"] = price_value
        
        # 할인 전 원가 (.ok-card__price-value--discounted)
        discounted_price = ""
        if price_section:
            discounted_elem = price_section.find('span', class_='ok-card__price-value--discounted')
            if discounted_elem:
                discounted_price = discounted_elem.get_text(strip=True)
        product["할인 전 원가"] = discounted_price
        
        # 별점 이미지 (고정값)
        product["별점 이미지"] = "./images/icon_start.svg"
        
        # 리뷰수 (.ok-star-ratings__ratings-reviewcount)
        review_count = ""
        review_elem = card_div.find(class_='ok-star-ratings__ratings-reviewcount')
        if review_elem:
            review_count = review_elem.get_text(strip=True)
        product["리뷰수"] = review_count
        
        # 카테고리 (.ok-card__snipe > span)
        category = ""
        snipe_elem = card_div.find('div', class_='ok-card__snipe')
        if snipe_elem:
            span_elem = snipe_elem.find('span')
            if span_elem:
                category = span_elem.get_text(strip=True)
        product["카테고리"] = category
        
        # 상품 이미지 (.ok-card__image-wrap img의 모든 src)
        image_urls = []
        image_wrap = card_div.find('div', class_='ok-card__image-wrap')
        if image_wrap:
            img_tags = image_wrap.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if src:
                    image_urls.append(src)
        product["상품 이미지"] = image_urls
        
        products.append(product)
    
    return products

def main():
    # 현재 디렉토리에서 여성-클로그_2.html 파일 찾기
    html_file = "여성-클로그_2.html"
    
    if not os.path.exists(html_file):
        print(f"파일을 찾을 수 없습니다: {html_file}")
        return
    
    print(f"HTML 파일에서 상품 정보를 추출 중: {html_file}")
    
    # 상품 정보 추출
    products = extract_products_from_html(html_file)
    
    if not products:
        print("추출된 상품이 없습니다.")
        return
    
    print(f"총 {len(products)}개의 상품을 추출했습니다.")
    
    # JSON 파일로 저장
    output_file = "여성-클로그_2.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"JSON 파일이 생성되었습니다: {output_file}")
    
    # 첫 번째 상품 정보 출력 (확인용)
    if products:
        print("\n첫 번째 상품 정보:")
        print(json.dumps(products[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()