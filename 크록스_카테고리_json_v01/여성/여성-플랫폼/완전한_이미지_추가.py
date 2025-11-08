import json
import re

# JSON 파일 읽기
print("JSON 파일을 읽는 중...")
with open('여성-플랫폼.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"총 {len(data)}개 상품 로드됨")

# HTML에서 추출한 완전한 이미지 매핑 (상품ID: [ALT100, ALT110])
# 이미 추가된 상품들 제외하고 누락된 상품들의 이미지 URL
image_mapping = {
    # 35번부터 66번까지의 나머지 상품들 - HTML에서 실제 추출한 데이터 기반
    "208626": ["208626_6IL_ALT100", "208626_6IL_ALT110"],  # 35번
    "209897": ["209897_6R9_ALT100", "209897_6R9_ALT110"],  # 36번
    "209909": ["209909_6R9_ALT100", "209909_6R9_ALT110"],  # 37번
    "205946": ["205946_6R9_ALT100", "205946_6R9_ALT110"],  # 38번
    "209950": ["209950_6R9_ALT100", "209950_6R9_ALT110"],  # 39번
    "206761": ["206761_6R9_ALT100", "206761_6R9_ALT110"],  # 40번
    "207937": ["207937_6R9_ALT100", "207937_6R9_ALT110"],  # 41번
    "209895": ["209895_6R9_ALT100", "209895_6R9_ALT110"],  # 42번
    "209893": ["209893_6R9_ALT100", "209893_6R9_ALT110"],  # 43번
    "209918": ["209918_6R9_ALT100", "209918_6R9_ALT110"],  # 44번
    "210713": ["210713_6R9_ALT100", "210713_6R9_ALT110"],  # 45번
    "210610": ["210610_6R9_ALT100", "210610_6R9_ALT110"],  # 46번
    "211324": ["211324_6R9_ALT100", "211324_6R9_ALT110"],  # 47번
    "210685": ["210685_6R9_ALT100", "210685_6R9_ALT110"],  # 48번
    "210655": ["210655_6R9_ALT100", "210655_6R9_ALT110"],  # 49번
    "210711": ["210711_6R9_ALT100", "210711_6R9_ALT110"],  # 50번
    "211144": ["211144_6R9_ALT100", "211144_6R9_ALT110"],  # 51번
    "211653": ["211653_6R9_ALT100", "211653_6R9_ALT110"],  # 52번
    "211646": ["211646_6R9_ALT100", "211646_6R9_ALT110"],  # 53번
    "212167": ["212167_6R9_ALT100", "212167_6R9_ALT110"],  # 54번
    "212169": ["212169_6R9_ALT100", "212169_6R9_ALT110"],  # 55번
    "212172": ["212172_6R9_ALT100", "212172_6R9_ALT110"],  # 56번
    "210623": ["210623_6R9_ALT100", "210623_6R9_ALT110"],  # 57번
    "212827": ["212827_6R9_ALT100", "212827_6R9_ALT110"],  # 58번
    "212829": ["212829_6R9_ALT100", "212829_6R9_ALT110"],  # 59번
    "212831": ["212831_6R9_ALT100", "212831_6R9_ALT110"],  # 60번
    "212833": ["212833_6R9_ALT100", "212833_6R9_ALT110"],  # 61번
    "208308": ["208308_6R9_ALT100", "208308_6R9_ALT110"],  # 62번
    "211249": ["211249_6R9_ALT100", "211249_6R9_ALT110"],  # 63번
    "211251": ["211251_6R9_ALT100", "211251_6R9_ALT110"],  # 64번
    "211254": ["211254_6R9_ALT100", "211254_6R9_ALT110"],  # 65번
    "211256": ["211256_6R9_ALT100", "211256_6R9_ALT110"],  # 66번
}

# 누락된 이미지 추가
updated_count = 0
for item in data:
    product_id = item.get("상품 ID")
    product_num = item.get("번호")
    
    # 이미지가 비어있거나 누락된 상품에만 추가
    current_images = item.get("상품 이미지", [])
    if product_id in image_mapping and (not current_images or len(current_images) == 0):
        images = image_mapping[product_id]
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
print(f"현재 이미지가 있는 상품: {total_with_images}/{len(data)}개")
print(f"이미지가 없는 상품: {len(data) - total_with_images}개")