import json
import requests
import os
import re
from urllib.parse import urlparse
from pathlib import Path

def sanitize_filename(filename):
    """파일명에서 특수문자 제거"""
    # 윈도우에서 사용할 수 없는 문자들 제거
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 연속된 언더스코어를 하나로 변경
    filename = re.sub(r'_+', '_', filename)
    # 앞뒤 공백과 점 제거
    filename = filename.strip(' .')
    return filename

def download_image(url, save_path, timeout=30):
    """이미지 다운로드"""
    try:
        # User-Agent 헤더 추가 (일부 사이트에서 bot 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 다운로드 완료: {os.path.basename(save_path)}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 다운로드 실패: {url}")
        print(f"   오류: {e}")
        return False

def process_images_and_update_json():
    """이미지 다운로드 및 JSON 업데이트"""
    
    # JSON 파일 읽기
    json_file = "여성-플립_슬라이드.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    
    total_images = 0
    downloaded_images = 0
    
    # 각 상품 처리
    for product in products:
        product_num = product.get("번호", "")
        product_name = product.get("상품명", "")
        image_urls = product.get("상품 이미지", [])
        
        if not image_urls:
            continue
            
        new_image_paths = []
        
        for idx, url in enumerate(image_urls):
            total_images += 1
            
            # 파일 확장자 추출 (기본값: jpg)
            parsed_url = urlparse(url)
            file_ext = ".jpg"  # 크록스 이미지는 대부분 jpg로 변환됨
            
            # 파일명 생성: 번호_상품명_이미지순번
            safe_product_name = sanitize_filename(product_name)
            filename = f"{product_num}_{safe_product_name}_{idx+1}{file_ext}"
            
            # 저장 경로
            save_path = os.path.join(images_dir, filename)
            
            # 이미지 다운로드
            if download_image(url, save_path):
                downloaded_images += 1
                # 로컬 경로로 변경 (상대 경로 사용)
                local_path = f"./images/{filename}"
                new_image_paths.append(local_path)
                
                print(f"   상품 {product_num}: {filename}")
            else:
                # 다운로드 실패시 원본 URL 유지
                new_image_paths.append(url)
        
        # 상품 이미지 경로 업데이트
        product["상품 이미지"] = new_image_paths
    
    # 업데이트된 JSON 저장
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 다운로드 완료 요약:")
    print(f"   전체 이미지: {total_images}개")
    print(f"   성공: {downloaded_images}개")
    print(f"   실패: {total_images - downloaded_images}개")
    print(f"\n💾 JSON 파일이 업데이트되었습니다: {json_file}")
    
    return downloaded_images, total_images

if __name__ == "__main__":
    print("🖼️  상품 이미지 다운로드 시작...\n")
    
    try:
        downloaded, total = process_images_and_update_json()
        
        if downloaded > 0:
            print(f"\n✅ 이미지 다운로드 및 JSON 업데이트가 완료되었습니다!")
            print(f"   images 폴더에 {downloaded}개의 이미지가 저장되었습니다.")
        else:
            print("\n⚠️  다운로드된 이미지가 없습니다.")
            
    except FileNotFoundError:
        print("❌ JSON 파일을 찾을 수 없습니다: 여성-플립_슬라이드.json")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")