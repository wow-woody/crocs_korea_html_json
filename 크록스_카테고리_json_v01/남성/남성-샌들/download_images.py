import json
import requests
import os
from urllib.parse import urlparse
import re

def sanitize_filename(filename):
    """파일명에서 사용할 수 없는 문자를 제거하고 공백을 언더스코어로 변경"""
    # 공백을 언더스코어로 변경
    filename = filename.replace(' ', '_')
    # 파일명에 사용할 수 없는 특수문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename

def download_image(url, save_path):
    """이미지를 다운로드하는 함수"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"이미지 다운로드 실패: {url} - {e}")
        return False

def download_all_images():
    # JSON 파일 읽기
    with open('남성-샌들.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # images 폴더 생성
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # 각 상품의 이미지 다운로드 및 JSON 업데이트
    for product in products:
        product_number = product["번호"]
        product_name = sanitize_filename(product["상품명"])
        images = product["상품 이미지"]
        
        new_image_paths = []
        
        for i, image_url in enumerate(images):
            if not image_url:  # 빈 URL 건너뛰기
                continue
                
            # 파일 확장자 추출 (기본적으로 jpg 사용)
            parsed_url = urlparse(image_url)
            file_extension = '.jpg'  # 크록스 이미지는 보통 jpg
            
            # 파일명 생성: 번호_상품명_순서
            filename = f"{product_number}_{product_name}_{i+1}{file_extension}"
            save_path = os.path.join('images', filename)
            
            print(f"다운로드 중: {filename}")
            
            # 이미지 다운로드
            if download_image(image_url, save_path):
                # 로컬 경로로 변경 (상대 경로)
                local_path = f"./images/{filename}"
                new_image_paths.append(local_path)
                print(f"다운로드 완료: {filename}")
            else:
                print(f"다운로드 실패: {filename}")
        
        # JSON의 상품 이미지 경로를 로컬 경로로 업데이트
        product["상품 이미지"] = new_image_paths
    
    # 업데이트된 JSON 파일 저장
    with open('남성-샌들.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print(f"\n모든 이미지 다운로드 완료!")
    print(f"JSON 파일이 로컬 이미지 경로로 업데이트되었습니다.")

if __name__ == "__main__":
    download_all_images()