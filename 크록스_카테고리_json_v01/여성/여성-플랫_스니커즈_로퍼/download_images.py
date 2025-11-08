#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
import re
from urllib.parse import urlparse

def sanitize_filename(filename):
    """파일명에 사용할 수 없는 문자를 제거"""
    # Windows에서 사용할 수 없는 문자들 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 연속된 공백을 하나로
    filename = re.sub(r'\s+', '_', filename)
    # 앞뒤 공백과 점 제거
    filename = filename.strip('. ')
    return filename

def download_image(url, save_path, timeout=30):
    """이미지를 다운로드하고 저장"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return True
    except Exception as e:
        print(f"❌ 이미지 다운로드 실패: {url}")
        print(f"   오류: {str(e)}")
        return False

def process_product_images(json_file_path):
    """JSON 파일의 모든 상품 이미지를 다운로드하고 로컬 경로로 업데이트"""
    
    # images 폴더 생성
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 '{images_dir}' 폴더를 생성했습니다.")
    
    # JSON 파일 읽기
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ JSON 파일 읽기 실패: {str(e)}")
        return
    
    total_images = 0
    downloaded_images = 0
    
    # 각 상품의 이미지 처리
    for product in products:
        product_num = product.get("번호", "")
        product_name = product.get("상품명", "")
        images = product.get("상품 이미지", [])
        
        if not images:
            continue
        
        new_image_paths = []
        
        for i, image_url in enumerate(images):
            total_images += 1
            
            # 파일명 생성: 번호_상품명_순서.jpg
            safe_product_name = sanitize_filename(product_name)
            filename = f"{product_num}_{safe_product_name}_{i+1}.jpg"
            save_path = os.path.join(images_dir, filename)
            
            print(f"📥 다운로드 중: {filename}")
            print(f"   URL: {image_url}")
            
            # 이미지 다운로드
            if download_image(image_url, save_path):
                # 상대 경로로 저장 (./images/파일명.jpg)
                local_path = f"./images/{filename}"
                new_image_paths.append(local_path)
                downloaded_images += 1
                print(f"✅ 성공: {local_path}")
            else:
                # 다운로드 실패 시 원본 URL 유지
                new_image_paths.append(image_url)
                print(f"🔄 원본 URL 유지: {image_url}")
            
            print("")  # 줄바꿈
        
        # 상품의 이미지 경로 업데이트
        product["상품 이미지"] = new_image_paths
    
    # 업데이트된 JSON 파일 저장
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"🎉 완료!")
        print(f"📊 총 이미지: {total_images}개")
        print(f"✅ 다운로드 성공: {downloaded_images}개")
        print(f"❌ 다운로드 실패: {total_images - downloaded_images}개")
        print(f"📝 JSON 파일이 업데이트되었습니다: {json_file_path}")
        
        # 첫 번째 상품의 업데이트된 이미지 경로 미리보기
        if products:
            print(f"\n📋 첫 번째 상품 이미지 경로 미리보기:")
            first_product = products[0]
            print(f"   상품명: {first_product.get('상품명', '')}")
            for img_path in first_product.get('상품 이미지', []):
                print(f"   - {img_path}")
    
    except Exception as e:
        print(f"❌ JSON 파일 저장 실패: {str(e)}")

def main():
    json_file = "여성-플랫_스니커즈_로퍼.json"
    
    if not os.path.exists(json_file):
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_file}")
        return
    
    print(f"🚀 상품 이미지 다운로드 시작...")
    print(f"📂 JSON 파일: {json_file}")
    print(f"📁 이미지 저장 폴더: ./images/")
    print(f"📝 파일명 형식: 번호_상품명_순서.jpg")
    print("-" * 50)
    
    process_product_images(json_file)

if __name__ == "__main__":
    main()