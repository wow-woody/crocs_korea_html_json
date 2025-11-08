import json
import requests
import os
import re

def download_all_images():
    # JSON 파일 읽기
    with open('크록스_상품목록_최종.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # images 폴더 생성
    os.makedirs('images', exist_ok=True)
    
    downloaded_count = 0
    failed_count = 0
    
    print(f"총 {len(products)}개 상품의 이미지를 다운로드합니다...")
    
    for i, product in enumerate(products, 1):
        product_number = product["번호"]
        product_name = product["상품명"]
        product_images = product.get("상품 이미지", [])
        
        # 상품명 정리
        clean_name = re.sub(r'[<>:"/\\|?*]', '', product_name)
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        print(f"[{i}/{len(products)}] 상품 {product_number}: {product_name}")
        
        for j, image_url in enumerate(product_images, 1):
            filename = f"{product_number}_{clean_name}_{j}.jpg"
            filepath = os.path.join('images', filename)
            
            if not os.path.exists(filepath):
                try:
                    print(f"  다운로드 중: {filename}")
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  완료: {filename}")
                    downloaded_count += 1
                    
                except Exception as e:
                    print(f"  실패: {filename} - {str(e)}")
                    failed_count += 1
            else:
                print(f"  이미 존재: {filename}")
    
    print(f"다운로드 완료! 성공: {downloaded_count}, 실패: {failed_count}")

if __name__ == "__main__":
    download_all_images()