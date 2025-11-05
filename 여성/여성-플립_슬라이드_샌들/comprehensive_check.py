import json
import os
from collections import defaultdict

def comprehensive_final_check():
    """전체 작업에 대한 종합적인 최종 확인"""
    
    print("🔍 === 전체 작업 최종 확인 ===\n")
    
    # 1. 파일 존재 확인
    print("📁 파일 존재 확인:")
    required_files = {
        "여성-플립_슬라이드.html": "원본 HTML",
        "여성-샌들.html": "원본 HTML", 
        "여성-플립_슬라이드.json": "플립/슬라이드 JSON",
        "여성-샌들.json": "샌들 JSON"
    }
    
    for file_path, description in required_files.items():
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {description}: {file_path}")
    
    # 2. images 폴더 확인
    print(f"\n🖼️  images 폴더 확인:")
    if os.path.exists("images"):
        files = os.listdir("images")
        jpg_files = [f for f in files if f.endswith('.jpg')]
        
        print(f"   ✅ 폴더 존재: images/")
        print(f"   📊 총 이미지 파일: {len(jpg_files)}개")
        
        # 공백 검사
        space_files = [f for f in jpg_files if ' ' in f]
        print(f"   🔤 공백 포함 파일: {len(space_files)}개")
        
        # 파일 크기 확인
        total_size = sum(os.path.getsize(os.path.join("images", f)) for f in jpg_files)
        print(f"   💾 총 파일 크기: {total_size/1024/1024:.2f} MB")
    else:
        print("   ❌ images 폴더가 존재하지 않습니다!")
        return
    
    # 3. JSON 데이터 분석
    print(f"\n📋 JSON 데이터 분석:")
    
    # 플립/슬라이드 JSON
    try:
        with open("여성-플립_슬라이드.json", 'r', encoding='utf-8') as f:
            flip_data = json.load(f)
        
        print(f"   플립/슬라이드:")
        print(f"     - 상품 수: {len(flip_data)}개")
        print(f"     - 번호 범위: {flip_data[0]['번호']}~{flip_data[-1]['번호']}")
        
        # 이미지 개수 확인
        flip_images = sum(len(product['상품 이미지']) for product in flip_data)
        print(f"     - 총 이미지: {flip_images}개")
        
    except Exception as e:
        print(f"   ❌ 플립/슬라이드 JSON 읽기 실패: {e}")
        flip_data = []
        flip_images = 0
    
    # 샌들 JSON
    try:
        with open("여성-샌들.json", 'r', encoding='utf-8') as f:
            sandal_data = json.load(f)
        
        print(f"   샌들:")
        print(f"     - 상품 수: {len(sandal_data)}개")
        print(f"     - 번호 범위: {sandal_data[0]['번호']}~{sandal_data[-1]['번호']}")
        
        # 이미지 개수 확인
        sandal_images = sum(len(product['상품 이미지']) for product in sandal_data)
        print(f"     - 총 이미지: {sandal_images}개")
        
    except Exception as e:
        print(f"   ❌ 샌들 JSON 읽기 실패: {e}")
        sandal_data = []
        sandal_images = 0
    
    # 4. 데이터 무결성 검사
    print(f"\n🔧 데이터 무결성 검사:")
    
    total_expected_images = flip_images + sandal_images
    print(f"   예상 이미지 수: {total_expected_images}개")
    print(f"   실제 파일 수: {len(jpg_files)}개")
    
    if total_expected_images == len(jpg_files):
        print(f"   ✅ 이미지 개수 일치!")
    else:
        print(f"   ❌ 이미지 개수 불일치!")
    
    # 5. 이미지 경로 검증
    print(f"\n🔗 이미지 경로 검증:")
    
    missing_files = []
    remote_urls = []
    
    all_products = flip_data + sandal_data
    for product in all_products:
        for img_path in product.get('상품 이미지', []):
            if img_path.startswith('./images/'):
                file_path = img_path[2:]  # './' 제거
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            elif img_path.startswith('http'):
                remote_urls.append(img_path)
    
    print(f"   로컬 이미지 파일 누락: {len(missing_files)}개")
    print(f"   원격 URL 잔여: {len(remote_urls)}개")
    
    if missing_files:
        print("   ❌ 누락된 파일들:")
        for f in missing_files[:5]:  # 최대 5개만 표시
            print(f"     - {f}")
        if len(missing_files) > 5:
            print(f"     ... 외 {len(missing_files)-5}개")
    
    if remote_urls:
        print("   ⚠️  원격 URL이 남아있습니다:")
        for url in remote_urls[:3]:  # 최대 3개만 표시
            print(f"     - {url}")
        if len(remote_urls) > 3:
            print(f"     ... 외 {len(remote_urls)-3}개")
    
    # 6. 샘플 데이터 검증
    print(f"\n📝 샘플 데이터 검증:")
    
    if flip_data:
        sample_flip = flip_data[0]
        print(f"   플립/슬라이드 첫 상품:")
        print(f"     번호: {sample_flip.get('번호')}")
        print(f"     상품명: {sample_flip.get('상품명')}")
        print(f"     이미지: {len(sample_flip.get('상품 이미지', []))}개")
        print(f"     첫 이미지: {sample_flip.get('상품 이미지', ['없음'])[0]}")
    
    if sandal_data:
        sample_sandal = sandal_data[0]
        print(f"   샌들 첫 상품:")
        print(f"     번호: {sample_sandal.get('번호')}")
        print(f"     상품명: {sample_sandal.get('상품명')}")
        print(f"     이미지: {len(sample_sandal.get('상품 이미지', []))}개")
        print(f"     첫 이미지: {sample_sandal.get('상품 이미지', ['없음'])[0]}")
    
    # 7. 최종 결과
    print(f"\n🎯 최종 결과 요약:")
    
    success_criteria = [
        (len(flip_data) == 17, "플립/슬라이드 17개 상품"),
        (len(sandal_data) == 18, "샌들 18개 상품"),
        (len(jpg_files) == 70, "총 70개 이미지 파일"),
        (len(space_files) == 0, "공백 없는 파일명"),
        (len(missing_files) == 0, "모든 이미지 파일 존재"),
        (len(remote_urls) == 0, "모든 URL 로컬 경로 변환"),
        (total_expected_images == len(jpg_files), "이미지 개수 일치")
    ]
    
    passed = sum(1 for condition, _ in success_criteria if condition)
    total = len(success_criteria)
    
    print(f"   성공한 검사: {passed}/{total}개")
    
    for condition, description in success_criteria:
        status = "✅" if condition else "❌"
        print(f"   {status} {description}")
    
    # 최종 판정
    if passed == total:
        print(f"\n🎉 전체 작업 완벽 완료! 모든 검사 통과!")
        print(f"   - HTML 파싱: 완료")
        print(f"   - 이미지 다운로드: 완료")
        print(f"   - 파일명 정리: 완료")
        print(f"   - JSON 업데이트: 완료")
    else:
        print(f"\n⚠️  일부 문제가 발견되었습니다. ({passed}/{total})")
        print(f"   위의 ❌ 항목들을 확인해주세요.")
    
    return passed == total

if __name__ == "__main__":
    comprehensive_final_check()