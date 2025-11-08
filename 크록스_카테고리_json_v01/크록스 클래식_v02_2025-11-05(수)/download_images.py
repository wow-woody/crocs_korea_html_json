import json
import requests
import os
import re
from urllib.parse import urlparse

# JSON 파일 읽기
with open('크록스_상품목록_최종.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# images 폴더 생성
if not os.path.exists('images'):
    os.makedirs('images')

total_products = len(products)
downloaded_count = 0
failed_count = 0

print(f"총 {total_products}개 상품의 이미지를 다운로드합니다...")

for i, product in enumerate(products, 1):
    product_number = product["번호"]
    product_name = product["상품명"]
    product_images = product.get("상품 이미지", [])
    
    # 상품명에서 특수문자 제거 및 공백을 _로 변경
    clean_name = re.sub(r'[<>:"/\\|?*]', '', product_name)
    clean_name = re.sub(r'\s+', '_', clean_name)
    
    print(f"[{i}/{total_products}] 상품 {product_number}: {product_name}")
    
    if product_images:
        for j, image_url in enumerate(product_images, 1):
            try:
                # 파일명 생성: 번호_상품명_순번
                filename = f"{product_number}_{clean_name}_{j}.jpg"
                filepath = os.path.join('images', filename)
                
                # 파일이 이미 존재하는지 확인
                if not os.path.exists(filepath):
                    print(f"  이미지 {j} 다운로드 중: {filename}")
                    
                    # 이미지 다운로드
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    # 파일 저장
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  ✓ 다운로드 완료: {filename}")
                    downloaded_count += 1
                else:
                    print(f"  ⚠ 파일 이미 존재: {filename}")
                    
            except Exception as e:
                print(f"  ✗ 다운로드 실패: {image_url}")
                print(f"    오류: {str(e)}")
                failed_count += 1
    else:
        print("  ⚠ 이미지 URL이 없습니다.")
    
    # 진행률 표시
    progress = round((i / total_products) * 100, 1)
    print(f"진행률: {progress}% ({i}/{total_products})")
    print("-" * 50)

print(f"이미지 다운로드 완료!")
print(f"다운로드 성공: {downloaded_count}개")
print(f"다운로드 실패: {failed_count}개")