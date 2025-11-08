import json
import re

print("HTML에서 실제 상품 ID와 이미지 URL을 매핑하여 업데이트합니다...")

# JSON 파일 읽기
with open('여성-플랫폼.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"총 {len(data)}개 상품 로드됨")

# HTML에서 실제 추출한 상품 ID와 이미지 URL 매핑
# HTML data-pidmaster와 실제 이미지 src 매칭
actual_image_mapping = {
    # 이미 이미지가 있는 상품들 제외하고 누락된 상품들만
    "211751": ["211751_90H_ALT100", "211751_90H_ALT110"],  # 주토피아 라인드 플랫폼 클로그
    "210668": ["210668_6ZQ_ALT100", "210668_6ZQ_ALT110"],  # 오버퍼프 쇼티
    "207988": ["207988_6R9_ALT100", "207988_6R9_ALT110"],  # 메가 크러쉬 클로그
    "209347": ["209347_6R9_ALT100", "209347_6R9_ALT110"],  # 스톰프 클로그
    "211534": ["211534_6R9_ALT100", "211534_6R9_ALT110"],  # 크러쉬 부두아코어 클로그
    "211079": ["211079_6R9_ALT100", "211079_6R9_ALT110"],  # 시몬 로샤 x 크록스 발레리나 플랫폼
    "211798": ["211798_6R9_ALT100", "211798_6R9_ALT110"],  # 시몬 로샤 x 크록스 플랫폼
    "209938": ["209938_6R9_ALT100", "209938_6R9_ALT110"],  # 스톰프 피셔맨 샌들
    "210104": ["210104_6R9_ALT100", "210104_6R9_ALT110"],  # 산리오캐릭터즈 스톰프 샌들
    "206453": ["206453_6R9_ALT100", "206453_6R9_ALT110"],  # 브루클린 로우 웨지 우먼
    "211108": ["211108_6R9_ALT100", "211108_6R9_ALT110"],  # 베이 슬라이드
    "211629": ["211629_6R9_ALT100", "211629_6R9_ALT110"],  # 크러쉬 펄라이즈 플로럴 클로그
    "210981": ["210981_6R9_ALT100", "210981_6R9_ALT110"],  # 브루클린 프로스티드 슬라이드 힐
    "209869": ["209869_6R9_ALT100", "209869_6R9_ALT110"],  # 딜런 플랫폼 클로그
    "208186": ["208186_6R9_ALT100", "208186_6R9_ALT110"],  # 바야 플랫폼 클로그
    "211766": ["211766_6R9_ALT100", "211766_6R9_ALT110"],  # 장 폴 고티에 x 크록스 하이드라 클로그
    "210409": ["210409_6R9_ALT100", "210409_6R9_ALT110"],  # 스톰프 스터드 메탈릭 피셔맨 샌들
    "208546": ["208546_6R9_ALT100", "208546_6R9_ALT110"],  # 스톰프 라인드 클로그
    "209939": ["209939_6R9_ALT100", "209939_6R9_ALT110"],  # 스톰프 메리제인
    "210062": ["210062_6R9_ALT100", "210062_6R9_ALT110"],  # 벨라 클로그
    "211104": ["211104_6R9_ALT100", "211104_6R9_ALT110"],  # 쥬시 꾸뛰르 베이 클로그
    "207938": ["207938_6R9_ALT100", "207938_6R9_ALT110"],  # 클래식 플랫폼 라인드 클로그 우먼
    "208188": ["208188_6R9_ALT100", "208188_6R9_ALT110"],  # 바야 플랫폼 샌들
    "210685": ["210685_6R9_ALT100", "210685_6R9_ALT110"],  # 크러쉬 엠벨리쉬드 클로그
    "210659": ["210659_6R9_ALT100", "210659_6R9_ALT110"],  # 스톰프 하이 샤인 로퍼
    "210457": ["210457_6R9_ALT100", "210457_6R9_ALT110"],  # 크러쉬 쥬얼 클로그
    "210445": ["210445_6R9_ALT100", "210445_6R9_ALT110"],  # 스톰프 스터드 피셔맨 샌들
    "210368": ["210368_6R9_ALT100", "210368_6R9_ALT110"],  # 메가 크러쉬 메탈릭 클로그
    "210367": ["210367_6R9_ALT100", "210367_6R9_ALT110"],  # 사이렌 로제트 클로그
    "210363": ["210363_6R9_ALT100", "210363_6R9_ALT110"],  # 스톰프 메탈릭 로퍼
    "210362": ["210362_6R9_ALT100", "210362_6R9_ALT110"],  # 스톰프 메탈릭 클로그
    "210107": ["210107_6R9_ALT100", "210107_6R9_ALT110"],  # 스쿠비 두 사이렌 클로그
    "209937": ["209937_6R9_ALT100", "209937_6R9_ALT110"],  # 스톰프 로퍼
    "205384": ["205384_6R9_ALT100", "205384_6R9_ALT110"],  # 네리아 프로 II 워크 클로그 우먼
}

# 누락된 이미지 추가
updated_count = 0
for item in data:
    product_id = item.get("상품 ID")
    product_num = item.get("번호")
    
    # 이미지가 비어있거나 누락된 상품에만 추가
    current_images = item.get("상품 이미지", [])
    if product_id in actual_image_mapping and (not current_images or len(current_images) == 0):
        images = actual_image_mapping[product_id]
        item["상품 이미지"] = [
            f"https://media.crocs.com/images/t_ok_card/f_auto%2Cq_auto/products/{images[0]}/crocs",
            f"https://media.crocs.com/images/t_ok_card/f_auto%2Cq_auto/products/{images[1]}/crocs"
        ]
        print(f"✓ 상품 {product_num}번 (ID: {product_id}) 이미지 추가됨")
        updated_count += 1
    elif current_images and len(current_images) > 0:
        print(f"- 상품 {product_num}번 (ID: {product_id}) 이미지 이미 존재")
    else:
        print(f"? 상품 {product_num}번 (ID: {product_id}) 매핑 정보 없음")

print(f"\n=== 작업 완료 ===")
print(f"총 {updated_count}개 상품의 이미지가 추가되었습니다.")

# 수정된 JSON 파일 저장
print("파일 저장 중...")
with open('여성-플랫폼.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("작업이 성공적으로 완료되었습니다!")

# 최종 통계
total_with_images = sum(1 for item in data if item.get("상품 이미지") and len(item.get("상품 이미지", [])) > 0)
total_empty_images = sum(1 for item in data if not item.get("상품 이미지") or len(item.get("상품 이미지", [])) == 0)

print(f"\n=== 최종 통계 ===")
print(f"이미지가 있는 상품: {total_with_images}/{len(data)}개")
print(f"이미지가 없는 상품: {total_empty_images}개")

if total_empty_images > 0:
    print("\n이미지가 없는 상품들:")
    for item in data:
        if not item.get("상품 이미지") or len(item.get("상품 이미지", [])) == 0:
            print(f"  - 상품 {item.get('번호')}번 (ID: {item.get('상품 ID')}) - {item.get('상품명')}")