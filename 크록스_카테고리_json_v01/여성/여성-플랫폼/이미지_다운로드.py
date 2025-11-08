import json
import urllib.request
import os
import re
from urllib.parse import urlparse

print("이미지 다운로드 및 로컬 경로 교체 작업을 시작합니다...")

# JSON 파일 읽기
with open('여성-플랫폼.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"총 {len(data)}개 상품 로드됨")

# images 폴더 생성 (이미 생성됨)
images_dir = "images"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    print(f"'{images_dir}' 폴더 생성됨")

def sanitize_filename(filename):
    """파일명에서 사용할 수 없는 문자 제거"""
    # Windows에서 사용할 수 없는 문자들 제거
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # 공백을 언더스코어로 변경
    filename = filename.replace(' ', '_')
    # 연속된 언더스코어를 하나로
    filename = re.sub(r'_+', '_', filename)
    return filename.strip('_')

def download_image(url, local_path):
    """이미지 다운로드 함수"""
    try:
        # User-Agent 헤더 추가 (일부 웹사이트에서 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            with open(local_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  ❌ 다운로드 실패: {e}")
        return False

# 각 상품의 이미지 다운로드 및 경로 교체
total_images = 0
downloaded_images = 0
failed_images = 0

for item in data:
    product_num = item.get("번호")
    product_name = item.get("상품명", "")
    product_images = item.get("상품 이미지", [])
    
    if not product_images:
        print(f"상품 {product_num}번: 이미지 없음")
        continue
    
    print(f"\n상품 {product_num}번 '{product_name}' 이미지 다운로드 중...")
    
    # 상품명을 파일명으로 사용할 수 있도록 정리
    safe_product_name = sanitize_filename(product_name)
    
    new_image_paths = []
    
    for i, image_url in enumerate(product_images):
        total_images += 1
        
        # 파일 확장자 추출 (일반적으로 .jpg로 가정)
        file_extension = ".jpg"
        
        # 로컬 파일명: "번호_상품명_순서번호.jpg"
        local_filename = f"{product_num}_{safe_product_name}_{i+1}{file_extension}"
        local_path = os.path.join(images_dir, local_filename)
        
        print(f"  이미지 {i+1}: {image_url}")
        print(f"  저장 경로: {local_path}")
        
        # 이미지 다운로드
        if download_image(image_url, local_path):
            print(f"  ✅ 다운로드 성공")
            # 로컬 경로를 상대 경로로 저장
            new_image_paths.append(f"./images/{local_filename}")
            downloaded_images += 1
        else:
            print(f"  ❌ 다운로드 실패")
            # 실패한 경우 원본 URL 유지
            new_image_paths.append(image_url)
            failed_images += 1
    
    # 이미지 경로를 로컬 경로로 교체
    item["상품 이미지"] = new_image_paths
    
    print(f"  상품 {product_num}번 완료: {len(new_image_paths)}개 이미지 처리됨")

print(f"\n=== 이미지 다운로드 완료 ===")
print(f"총 이미지 수: {total_images}개")
print(f"성공적으로 다운로드된 이미지: {downloaded_images}개")
print(f"다운로드 실패한 이미지: {failed_images}개")
print(f"성공률: {downloaded_images/total_images*100:.1f}%" if total_images > 0 else "0%")

# 수정된 JSON 파일 저장
print("\n업데이트된 JSON 파일 저장 중...")
with open('여성-플랫폼.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 모든 작업이 완료되었습니다!")
print(f"이미지들이 '{images_dir}' 폴더에 저장되었고,")
print("JSON 파일의 이미지 경로가 로컬 경로로 업데이트되었습니다.")