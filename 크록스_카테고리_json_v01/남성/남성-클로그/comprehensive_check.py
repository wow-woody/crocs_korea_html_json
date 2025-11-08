import json
import os
from pathlib import Path

def comprehensive_verification():
    """모든 상품의 이미지 경로를 전체 검증"""
    
    print("🔍 전체 상품 이미지 경로 검증 중...")
    
    # JSON 데이터 로드
    with open("남성-클로그.json", 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total_images = 0
    local_images = 0
    url_images = 0
    
    for product in products:
        images = product.get("상품 이미지", [])
        for img_path in images:
            total_images += 1
            if img_path.startswith("./images/"):
                local_images += 1
            else:
                url_images += 1
    
    print(f"📊 전체 이미지 경로 통계:")
    print(f"  총 이미지 경로: {total_images}개")
    print(f"  로컬 경로: {local_images}개")
    print(f"  URL 경로: {url_images}개")
    
    # images 폴더 파일 수
    images_dir = Path("images")
    image_files = list(images_dir.glob("*"))
    print(f"  실제 파일: {len(image_files)}개")
    
    # 모든 경로가 로컬로 변환되었는지 확인
    if url_images == 0:
        print("✅ 모든 이미지 경로가 로컬 주소로 변환되었습니다!")
    else:
        print(f"❌ {url_images}개의 이미지가 아직 URL 상태입니다")
    
    # 파일 수 일치 확인
    if local_images == len(image_files):
        print("✅ JSON의 로컬 경로 수와 실제 파일 수가 일치합니다!")
    else:
        print(f"⚠️ JSON 로컬 경로({local_images}개) ≠ 실제 파일({len(image_files)}개)")
    
    return url_images == 0 and local_images == len(image_files)

if __name__ == "__main__":
    success = comprehensive_verification()
    
    if success:
        print("\n🎉 완벽한 성공! 모든 요구사항이 충족되었습니다!")
    else:
        print("\n⚠️ 일부 확인이 필요한 부분이 있습니다")