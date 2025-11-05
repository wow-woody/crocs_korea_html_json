import json
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

def extract_products_from_html(html_file_path):
    """HTML 파일에서 상품 정보를 추출하여 JSON으로 변환"""
    
    # HTML 파일 읽기
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # .ok-card-list 내의 모든 li 요소 찾기
    card_list = soup.find('ul', class_='ok-card-list')
    if not card_list:
        print("ok-card-list를 찾을 수 없습니다.")
        return []
    
    products = []
    product_number = 1
    
    # 모든 li 태그 찾기 (빈 li는 제외)
    li_items = card_list.find_all('li')
    
    for li in li_items:
        # ok-card 클래스를 가진 div 찾기
        card = li.find('div', class_='ok-card')
        if not card:
            continue
            
        product_data = {}
        
        # 번호
        product_data['번호'] = product_number
        
        # 상품 ID (data-pidmaster 속성에서 추출)
        product_id = card.get('data-pidmaster', '')
        product_data['상품 ID'] = product_id
        
        # 상품명
        product_name_elem = card.find(class_='ok-card__product-name')
        product_name = product_name_elem.get_text(strip=True) if product_name_elem else ''
        product_data['상품명'] = product_name
        
        # 색상 정보 추출
        colors = []
        swatch_colors = card.find_all(class_='ok-card__swatch-color')
        for swatch in swatch_colors:
            style = swatch.get('style', '')
            if 'background:' in style or 'background-color:' in style:
                colors.append(style)
        product_data['색상'] = colors
        
        # 가격 정보 추출
        price_section = card.find(class_='ok-card__price')
        price_info = {}
        
        if price_section:
            # 할인가 할인율
            sale_price = price_section.find(class_='ok-card__price-value--sale')
            if sale_price:
                price_info['할인가_할인율'] = sale_price.get_text(strip=True)
            
            # 할인~ 
            price_to = price_section.find(class_='ok-card__price-to')
            if price_to:
                price_info['할인~'] = price_to.get_text(strip=True)
            
            # 일반 가격
            regular_price = price_section.find(class_='ok-card__price-value--bold')
            if regular_price and 'sale' not in regular_price.get('class', []):
                price_info['가격'] = regular_price.get_text(strip=True)
            
            # 할인 전 원가
            discounted_price = price_section.find(class_='ok-card__price-value--discounted')
            if discounted_price:
                price_info['할인_전_원가'] = discounted_price.get_text(strip=True)
            
            # 모든 가격 정보를 하나로 합치기
            all_prices = price_section.get_text(strip=True)
            price_info['전체_가격_정보'] = all_prices
        
        product_data.update(price_info)
        
        # 별점 이미지 (고정값)
        product_data['별점 이미지'] = './images/icon_start.svg'
        
        # 리뷰수
        review_count_elem = card.find(class_='ok-star-ratings__ratings-reviewcount')
        review_count = ''
        if review_count_elem:
            review_text = review_count_elem.get_text(strip=True)
            # 괄호 안의 숫자만 추출
            match = re.search(r'\((\d+)\)', review_text)
            if match:
                review_count = match.group(1)
        product_data['리뷰수'] = review_count
        
        # 카테고리
        snipe_elem = card.find(class_='ok-card__snipe')
        category = ''
        if snipe_elem:
            span_elem = snipe_elem.find('span')
            if span_elem:
                category = span_elem.get_text(strip=True)
        product_data['카테고리'] = category
        
        # 상품 이미지 URL들
        image_urls = []
        image_wrap = card.find(class_='ok-card__image-wrap')
        if image_wrap:
            images = image_wrap.find_all('img')
            for img in images:
                src = img.get('src', '')
                if src:
                    image_urls.append(src)
        
        product_data['상품 이미지'] = image_urls
        
        products.append(product_data)
        product_number += 1
    
    return products

def sanitize_filename(filename):
    """파일명에서 사용할 수 없는 문자를 제거하고 공백을 _로 변경"""
    # 윈도우에서 사용할 수 없는 문자들 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 공백을 언더스코어로 변경
    filename = filename.replace(' ', '_')
    return filename

def download_images(products, base_path):
    """상품 이미지들을 다운로드하고 로컬 경로로 업데이트"""
    
    # images 폴더 생성
    images_dir = os.path.join(base_path, 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"images 폴더 생성: {images_dir}")
    
    for product in products:
        image_urls = product.get('상품 이미지', [])
        local_image_paths = []
        
        for i, url in enumerate(image_urls):
            if not url:
                continue
                
            try:
                # 이미지 다운로드
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 파일 확장자 추출 (기본값은 .jpg)
                parsed_url = urlparse(url)
                file_ext = '.jpg'  # 기본 확장자
                
                # 파일명 생성: "번호"_"상품명"_이미지순서
                product_name = sanitize_filename(product.get('상품명', 'unknown'))
                filename = f"{product['번호']}_{product_name}_{i+1}{file_ext}"
                
                file_path = os.path.join(images_dir, filename)
                
                # 이미지 저장
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # 로컬 경로 추가 (상대 경로)
                local_path = f"./images/{filename}"
                local_image_paths.append(local_path)
                
                print(f"이미지 다운로드 완료: {filename}")
                
                # 요청 간격 (서버 부하 방지)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"이미지 다운로드 실패 {url}: {str(e)}")
                continue
        
        # 상품 이미지 경로를 로컬 경로로 업데이트
        product['상품 이미지'] = local_image_paths

def main():
    # 현재 스크립트 경로 기준으로 HTML 파일 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(base_path, '남성-스니커즈.html')
    
    if not os.path.exists(html_file):
        print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
        return
    
    print("HTML 파일에서 상품 정보 추출 중...")
    products = extract_products_from_html(html_file)
    
    if not products:
        print("추출된 상품이 없습니다.")
        return
    
    print(f"총 {len(products)}개의 상품을 추출했습니다.")
    
    # 이미지 다운로드
    print("이미지 다운로드 시작...")
    download_images(products, base_path)
    
    # JSON 파일로 저장
    json_file = os.path.join(base_path, '남성-스니커즈.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"JSON 파일 생성 완료: {json_file}")
    print("모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()