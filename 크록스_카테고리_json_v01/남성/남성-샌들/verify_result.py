import json

# JSON 파일 읽기
with open('남성-샌들.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*50)
print("최종 검증 결과")
print("="*50)

print(f"✅ 총 상품 수: {len(data)}")
print(f"✅ 첫 번째 상품의 모든 필드:")
for key in data[0].keys():
    print(f"   - {key}")
 
print(f"\n✅ 상품 ID 추출 확인 (처음 3개): {[p['상품 ID'] for p in data[:3]]}")
print(f"✅ 상품명 추출 확인 (처음 3개): {[p['상품명'] for p in data[:3]]}")
print(f"✅ 리뷰수 추출 확인 (처음 3개): {[p['리뷰수'] for p in data[:3]]}")

# 이미지 경로 확인
print(f"\n✅ 상품 이미지 로컬 경로 변경 확인:")
for i, product in enumerate(data[:3], 1):
    print(f"   상품 {i}: {len(product['상품 이미지'])}개 이미지")
    for img in product['상품 이미지']:
        if img.startswith('./images/'):
            print(f"      ✅ {img}")
        else:
            print(f"      ❌ {img}")

# 색상 정보 확인
print(f"\n✅ 색상 정보 추출 확인:")
for i, product in enumerate(data[:3], 1):
    print(f"   상품 {i}: {len(product['색상'])}개 색상")

print(f"\n✅ 가격 정보 추출 확인 (처음 3개):")
for i, product in enumerate(data[:3], 1):
    print(f"   상품 {i} - 가격: '{product['가격']}', 할인 전 원가: '{product['할인 전 원가']}'")

print("\n" + "="*50)
print("검증 완료!")
print("="*50)