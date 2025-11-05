import json
import os

def final_check():
    """최종 확인 검사"""
    
    print("🔍 === 최종 작업 결과 확인 ===\n")
    
    # 1. JSON 파일 로드
    try:
        with open('여성-플립_슬라이드.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print("❌ JSON 파일을 찾을 수 없습니다.")
        return
    
    # 2. 기본 정보 확인
    print(f"📊 기본 정보:")
    print(f"   총 상품 수: {len(products)}개")
    print(f"   JSON 파일 크기: {os.path.getsize('여성-플립_슬라이드.json')} bytes")
    
    # 3. 필드 구조 확인
    if products:
        fields = list(products[0].keys())
        print(f"   필드 수: {len(fields)}개")
        print(f"   필드 목록: {', '.join(fields)}")
    
    # 4. 이미지 정보 확인
    total_images = 0
    local_images = 0
    remote_images = 0
    
    print(f"\n🖼️  이미지 정보:")
    for product in products:
        images = product.get('상품 이미지', [])
        total_images += len(images)
        
        for img in images:
            if img.startswith('./images/'):
                local_images += 1
            elif img.startswith('http'):
                remote_images += 1
    
    print(f"   전체 이미지: {total_images}개")
    print(f"   로컬 이미지: {local_images}개")
    print(f"   원격 이미지: {remote_images}개")
    print(f"   변환 성공률: {(local_images/total_images)*100:.1f}%" if total_images > 0 else "0%")
    
    # 5. images 폴더 확인
    images_dir = "images"
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
        print(f"   실제 파일 수: {len(image_files)}개")
        
        # 파일 크기 확인
        total_size = sum(os.path.getsize(os.path.join(images_dir, f)) for f in image_files)
        print(f"   총 파일 크기: {total_size/1024/1024:.2f} MB")
    else:
        print("   ❌ images 폴더가 존재하지 않습니다.")
    
    # 6. 상품별 이미지 개수
    print(f"\n📋 상품별 이미지 개수:")
    for product in products:
        num = product.get('번호', '?')
        name = product.get('상품명', 'Unknown')
        img_count = len(product.get('상품 이미지', []))
        print(f"   상품 {num:2d}: {img_count}개 - {name}")
    
    # 7. 샘플 데이터 검증
    print(f"\n✅ 샘플 데이터 검증:")
    
    # 첫 번째 상품
    first = products[0]
    print(f"   첫 번째 상품:")
    print(f"     번호: {first.get('번호')}")
    print(f"     상품 ID: {first.get('상품 ID')}")
    print(f"     상품명: {first.get('상품명')}")
    print(f"     색상 수: {len(first.get('색상', []))}")
    print(f"     리뷰수: {first.get('리뷰수')}")
    print(f"     이미지: {first.get('상품 이미지', [])[0] if first.get('상품 이미지') else 'None'}")
    
    # 중간 상품 (가격 범위가 있는)
    middle = products[4]  # 5번 상품
    print(f"   5번 상품 (가격 범위):")
    print(f"     상품명: {middle.get('상품명')}")
    print(f"     할인가: {middle.get('할인가 할인율')}")
    print(f"     할인~: '{middle.get('할인~')}'")
    print(f"     할인가-2: {middle.get('할인가-2')}")
    print(f"     카테고리: {middle.get('카테고리')}")
    
    # 8. 파일 검증
    print(f"\n🔧 파일 검증:")
    missing_files = []
    for product in products:
        for img_path in product.get('상품 이미지', []):
            if img_path.startswith('./images/'):
                file_path = img_path[2:]  # './' 제거
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
    
    if missing_files:
        print(f"   ❌ 누락된 파일 {len(missing_files)}개:")
        for f in missing_files[:5]:  # 최대 5개만 표시
            print(f"     - {f}")
        if len(missing_files) > 5:
            print(f"     ... 외 {len(missing_files)-5}개")
    else:
        print(f"   ✅ 모든 이미지 파일이 존재합니다!")
    
    print(f"\n🎉 최종 결과: {'성공' if not missing_files and local_images == total_images else '일부 문제 발견'}")
    print(f"   - 상품 데이터 추출: ✅ 완료 ({len(products)}개)")
    print(f"   - 이미지 다운로드: {'✅ 완료' if local_images == total_images else '❌ 미완료'} ({local_images}/{total_images})")
    print(f"   - JSON 업데이트: {'✅ 완료' if remote_images == 0 else '❌ 미완료'}")

if __name__ == "__main__":
    final_check()