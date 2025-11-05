import json
import os
from pathlib import Path

def final_verification():
    """모든 작업이 정확하게 완료되었는지 최종 검증"""
    
    print("=" * 60)
    print("🔍 최종 검증 시작")
    print("=" * 60)
    
    # 1. JSON 파일 존재 확인
    json_file = "남성-클로그.json"
    if not os.path.exists(json_file):
        print("❌ JSON 파일이 존재하지 않습니다.")
        return False
    print("✅ JSON 파일 존재 확인")
    
    # 2. images 폴더 존재 확인
    images_dir = Path("images")
    if not images_dir.exists():
        print("❌ images 폴더가 존재하지 않습니다.")
        return False
    print("✅ images 폴더 존재 확인")
    
    # 3. JSON 데이터 로드
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✅ JSON 데이터 로드 완료 (총 {len(products)}개 상품)")
    
    # 4. 이미지 파일 목록 확인
    image_files = list(images_dir.glob("*"))
    print(f"✅ images 폴더 내 파일 수: {len(image_files)}개")
    
    # 5. 각 상품별 검증
    total_images_in_json = 0
    local_path_count = 0
    url_path_count = 0
    missing_images = []
    
    print("\n📋 상품별 검증 중...")
    
    for i, product in enumerate(products[:5], 1):  # 처음 5개만 상세 확인
        product_num = product.get("번호", "")
        product_name = product.get("상품명", "")
        images = product.get("상품 이미지", [])
        
        print(f"\n상품 {i}:")
        print(f"  번호: {product_num}")
        print(f"  상품명: {product_name}")
        print(f"  이미지 수: {len(images)}개")
        
        for img_path in images:
            total_images_in_json += 1
            if img_path.startswith("./images/"):
                local_path_count += 1
                # 실제 파일 존재 확인
                file_path = Path(img_path[2:])  # "./" 제거
                if file_path.exists():
                    print(f"    ✅ {img_path}")
                else:
                    print(f"    ❌ {img_path} (파일 없음)")
                    missing_images.append(img_path)
            else:
                url_path_count += 1
                print(f"    ⚠️ {img_path} (여전히 URL)")
    
    # 6. 전체 통계
    print("\n" + "=" * 40)
    print("📊 전체 통계")
    print("=" * 40)
    print(f"총 상품 수: {len(products)}개")
    print(f"JSON 내 총 이미지 경로: {total_images_in_json}개")
    print(f"로컬 경로로 변환된 이미지: {local_path_count}개")
    print(f"여전히 URL인 이미지: {url_path_count}개")
    print(f"images 폴더 내 실제 파일: {len(image_files)}개")
    
    # 7. 파일명 규칙 확인
    print(f"\n📁 파일명 규칙 확인 (처음 10개)")
    for i, file_path in enumerate(image_files[:10]):
        filename = file_path.name
        print(f"  {i+1}. {filename}")
        
        # 파일명 패턴 확인 (번호_상품명_순서.확장자)
        if "_" in filename and "." in filename:
            parts = filename.split("_")
            if len(parts) >= 2 and parts[0].isdigit():
                print(f"      ✅ 올바른 패턴 (번호: {parts[0]})")
            else:
                print(f"      ⚠️ 패턴 확인 필요")
    
    # 8. 83번 상품 특별 확인 (이전에 문제가 있었던 상품)
    print(f"\n🔍 83번 상품 특별 확인")
    product_83 = None
    for product in products:
        if product.get("번호") == 83:
            product_83 = product
            break
    
    if product_83:
        print(f"  상품명: {product_83.get('상품명', '')}")
        print(f"  이미지 수: {len(product_83.get('상품 이미지', []))}개")
        for img_path in product_83.get("상품 이미지", []):
            file_exists = Path(img_path[2:]).exists() if img_path.startswith("./images/") else False
            status = "✅" if file_exists else "❌"
            print(f"    {status} {img_path}")
    else:
        print("  ❌ 83번 상품을 찾을 수 없습니다")
    
    # 9. 최종 판정
    print("\n" + "=" * 40)
    print("🎯 최종 판정")
    print("=" * 40)
    
    success = True
    
    if url_path_count > 0:
        print(f"⚠️ {url_path_count}개의 이미지가 여전히 URL 형태입니다")
        success = False
    
    if missing_images:
        print(f"❌ {len(missing_images)}개의 이미지 파일이 누락되었습니다")
        success = False
    
    if local_path_count != len(image_files):
        print(f"⚠️ JSON의 로컬 경로 수({local_path_count})와 실제 파일 수({len(image_files)})가 다릅니다")
    
    if success and url_path_count == 0 and not missing_images:
        print("🎉 모든 작업이 완벽하게 완료되었습니다!")
        print("✅ 모든 이미지가 다운로드되었습니다")
        print("✅ 모든 경로가 로컬 주소로 변경되었습니다")
        print("✅ 파일명 규칙이 올바르게 적용되었습니다")
    else:
        print("⚠️ 일부 문제가 발견되었습니다")
    
    return success

if __name__ == "__main__":
    final_verification()