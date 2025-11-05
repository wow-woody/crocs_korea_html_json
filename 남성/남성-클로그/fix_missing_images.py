import json
import requests
import os
import re
from urllib.parse import urlparse
from pathlib import Path

def download_missing_images():
    """83번 상품의 누락된 이미지를 수동으로 다운로드"""
    
    # 83번 상품 이미지 URL들
    image_urls = [
        "https://media.crocs.com/images/t_ok_card/f_auto%2Cq_auto/products/205669_001_ALT100/crocs-bistro-pro-literide-clog-side-view",
        "https://media.crocs.com/images/t_ok_card/f_auto%2Cq_auto/products/205669_001_ALT110/crocs-bistro-pro-literide-clog-pair"
    ]
    
    # images 폴더 확인
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)
    
    # 83번 상품명을 안전한 파일명으로 변경
    safe_filename_base = "83_비스트로_프로_라이트라이드_워크_클로그"
    
    downloaded_paths = []
    
    for idx, url in enumerate(image_urls, 1):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 파일명 생성
            filename = f"{safe_filename_base}_{idx}.jpg"
            save_path = images_dir / filename
            local_path = f"./images/{filename}"
            
            # 파일 저장
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            downloaded_paths.append(local_path)
            print(f"✓ 다운로드 완료: {filename}")
            
        except Exception as e:
            print(f"✗ 다운로드 실패: {str(e)}")
            # 실패시 원본 URL 유지
            downloaded_paths.append(url)
    
    return downloaded_paths

def update_json_for_product_83(json_file_path, new_image_paths):
    """83번 상품의 이미지 경로를 JSON에서 업데이트"""
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # 83번 상품 찾기
    for product in products:
        if product.get("번호") == 83:
            product["상품 이미지"] = new_image_paths
            print(f"✓ 83번 상품 이미지 경로 업데이트 완료")
            break
    
    # JSON 파일 저장
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON 파일 업데이트 완료: {json_file_path}")

if __name__ == "__main__":
    print("83번 상품 이미지 다운로드 시작...")
    
    # 누락된 이미지 다운로드
    new_paths = download_missing_images()
    
    # JSON 업데이트
    update_json_for_product_83("남성-클로그.json", new_paths)
    
    print("작업 완료!")