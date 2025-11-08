#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request
import os
import re
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    """Windows에서 허용되지 않는 문자를 제거하여 파일명을 안전하게 만듭니다."""
    # Windows에서 허용되지 않는 문자들을 제거
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    # 연속된 언더스코어를 하나로 축약
    filename = re.sub(r'_+', '_', filename)
    # 앞뒤 공백과 점 제거
    filename = filename.strip(' .')
    return filename

def download_image(url, local_path):
    """이미지를 다운로드합니다."""
    try:
        urllib.request.urlretrieve(url, local_path)
        return True
    except Exception as e:
        print(f"  ❌ 다운로드 실패: {e}")
        return False

def extract_correct_image_urls_from_html():
    """HTML에서 올바른 이미지 URL을 다시 추출합니다."""
    with open('여성-플랫폼.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ok-card 요소들을 찾아서 순서대로 처리
    products_data = []
    ok_cards = soup.find_all('div', class_='ok-card')
    
    print(f"총 {len(ok_cards)}개의 ok-card 요소 발견")
    
    for idx, card in enumerate(ok_cards, 1):
        try:
            # 상품명 추출
            product_name_elem = card.find('div', class_='ok-card__product-name')
            if not product_name_elem:
                print(f"상품 {idx}번: 상품명을 찾을 수 없음")
                continue
            
            product_name = product_name_elem.get_text().strip()
            
            # 이미지 추출
            image_wrap = card.find('div', class_='ok-card__image-wrap')
            if not image_wrap:
                print(f"상품 {idx}번: 이미지 영역을 찾을 수 없음")
                continue
            
            images = image_wrap.find_all('img')
            image_urls = []
            
            for img in images:
                src = img.get('src')
                if src and 'media.crocs.com' in src:
                    image_urls.append(src)
            
            products_data.append({
                'index': idx,
                'name': product_name,
                'image_urls': image_urls
            })
            
            print(f"상품 {idx}번: {product_name} - {len(image_urls)}개 이미지")
            
        except Exception as e:
            print(f"상품 {idx}번 처리 중 오류: {e}")
            continue
    
    return products_data

def main():
    print("HTML에서 올바른 이미지 URL 재추출 시작...")
    
    # HTML에서 올바른 이미지 URL 추출
    html_products = extract_correct_image_urls_from_html()
    
    # 현재 JSON 파일 로드
    with open('여성-플랫폼.json', 'r', encoding='utf-8') as f:
        json_products = json.load(f)
    
    print(f"\nJSON 상품 수: {len(json_products)}")
    print(f"HTML 상품 수: {len(html_products)}")
    
    # 35번부터 66번까지 이미지 URL 수정 및 다운로드
    updated_count = 0
    
    for json_product in json_products:
        product_num = json_product['번호']
        
        # 35번 이후 상품만 처리
        if product_num < 35:
            continue
            
        # HTML에서 해당 상품의 올바른 이미지 URL 찾기
        html_product = None
        for hp in html_products:
            if hp['index'] == product_num:
                html_product = hp
                break
        
        if not html_product:
            print(f"상품 {product_num}번: HTML에서 찾을 수 없음")
            continue
        
        print(f"\n상품 {product_num}번 '{html_product['name']}' 이미지 처리 중...")
        
        # 이미지 URL 업데이트 및 다운로드
        new_image_paths = []
        
        for i, image_url in enumerate(html_product['image_urls'], 1):
            print(f"  이미지 {i}: {image_url}")
            
            # 로컬 파일명 생성
            safe_name = sanitize_filename(html_product['name'])
            local_filename = f"{product_num}_{safe_name}_{i}.jpg"
            local_path = f"images/{local_filename}"
            
            print(f"  저장 경로: {local_path}")
            
            # 이미지 다운로드
            if download_image(image_url, local_path):
                print(f"  ✅ 다운로드 성공")
                new_image_paths.append(f"./images/{local_filename}")
            else:
                print(f"  ❌ 다운로드 실패")
                # 실패해도 로컬 경로는 추가 (나중에 수동으로 처리할 수 있도록)
                new_image_paths.append(f"./images/{local_filename}")
        
        # JSON에 업데이트된 이미지 경로 저장
        json_product['상품 이미지'] = new_image_paths
        updated_count += 1
        
        print(f"  상품 {product_num}번 완료: {len(new_image_paths)}개 이미지 처리됨")
    
    # 업데이트된 JSON 저장
    with open('여성-플랫폼.json', 'w', encoding='utf-8') as f:
        json.dump(json_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 작업 완료!")
    print(f"수정된 상품 수: {updated_count}")
    print(f"JSON 파일이 업데이트되었습니다.")

if __name__ == "__main__":
    main()