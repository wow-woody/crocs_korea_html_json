import json
import requests
import os
import re
from urllib.parse import urlparse
from pathlib import Path

def sanitize_filename(filename):
    """파일명에서 특수문자 제거하고 공백을 '_'로 대체"""
    # 공백을 '_'로 대체
    filename = filename.replace(' ', '_')
    # 파일명에 사용할 수 없는 문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 연속된 '_'를 하나로 줄이기
    filename = re.sub(r'_+', '_', filename)
    return filename

def get_image_extension(url, content_type=None):
    """URL이나 Content-Type에서 이미지 확장자 추출"""
    # URL에서 확장자 추출 시도
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path and '.' in path:
        ext = os.path.splitext(path)[1]
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return ext
    
    # Content-Type에서 확장자 결정
    if content_type:
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'webp' in content_type:
            return '.webp'
    
    # 기본값
    return '.jpg'

def download_image(url, save_path):
    """이미지 다운로드"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ 다운로드 완료: {os.path.basename(save_path)}")
        return True
        
    except Exception as e:
        print(f"✗ 다운로드 실패 ({url}): {str(e)}")
        return False

def download_all_images_and_update_json(json_file_path):
    """JSON 파일의 모든 이미지를 다운로드하고 로컬 주소로 업데이트"""
    
    # images 폴더 생성
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    
    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total_images = 0
    downloaded_images = 0
    
    # 각 상품의 이미지 다운로드 및 경로 업데이트
    for product in products:
        product_num = product.get("번호", "")
        product_name = product.get("상품명", "")
        image_urls = product.get("상품 이미지", [])
        
        if not image_urls:
            continue
        
        # 파일명 기본 부분 생성 (번호_상품명)
        safe_product_name = sanitize_filename(product_name)
        base_filename = f"{product_num}_{safe_product_name}"
        
        new_image_paths = []
        
        for idx, image_url in enumerate(image_urls):
            total_images += 1
            
            # 이미지 확장자 결정
            try:
                # HEAD 요청으로 Content-Type 확인
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                head_response = requests.head(image_url, headers=headers, timeout=10)
                content_type = head_response.headers.get('content-type', '')
            except:
                content_type = ''
            
            extension = get_image_extension(image_url, content_type)
            
            # 파일명 생성 (번호_상품명_이미지순서)
            if len(image_urls) > 1:
                filename = f"{base_filename}_{idx+1}{extension}"
            else:
                filename = f"{base_filename}{extension}"
            
            # 저장 경로
            save_path = images_dir / filename
            local_path = f"./images/{filename}"
            
            # 이미지 다운로드
            if download_image(image_url, save_path):
                new_image_paths.append(local_path)
                downloaded_images += 1
            else:
                # 다운로드 실패 시 원본 URL 유지
                new_image_paths.append(image_url)
        
        # 상품 이미지 경로 업데이트
        product["상품 이미지"] = new_image_paths
    
    # 업데이트된 JSON 저장
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 다운로드 완료 ===")
    print(f"전체 이미지 수: {total_images}")
    print(f"성공 다운로드: {downloaded_images}")
    print(f"실패 다운로드: {total_images - downloaded_images}")
    print(f"JSON 파일 업데이트 완료: {json_file_path}")
    
    return downloaded_images, total_images

if __name__ == "__main__":
    json_file = "남성-클로그.json"
    
    print("이미지 다운로드 및 JSON 업데이트 시작...")
    print("=" * 50)
    
    downloaded, total = download_all_images_and_update_json(json_file)
    
    print("=" * 50)
    print("작업 완료!")
    
    # images 폴더의 파일 수 확인
    images_dir = Path("images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*"))
        print(f"images 폴더에 저장된 파일 수: {len(image_files)}")
        
        # 처음 5개 파일명 출력
        print("\n처음 5개 다운로드된 이미지:")
        for i, file_path in enumerate(image_files[:5]):
            print(f"  {i+1}. {file_path.name}")