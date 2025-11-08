import json
import re
import os

def clean_price(price_str):
    """가격에서 ₩ 기호와 쉼표 제거하는 함수"""
    if not price_str or price_str == '':
        return ''
    # ₩25,900 -> 25900
    # ₩19,900 (23%) -> 19900 (23%)
    return re.sub(r'₩([\d,]+)', lambda m: m.group(1).replace(',', ''), price_str)

# 현재 디렉토리에서 신상 폴더의 JSON 파일 읽기
input_file = os.path.join("지비츠™ 참-신상", "지비츠_참-신상.json")
output_file = os.path.join("지비츠™ 참-신상", "지비츠_참-신상_v02.json")

try:
    # 원본 JSON 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 데이터 변환
    transformed_data = []
    for item in data:
        new_item = {
            'id': item['상품 ID'],
            'product': item['상품명'],
            'price': clean_price(item['가격']),
            'price_dc_rate': clean_price(item['할인가 할인율']),
            'price_cost': clean_price(item['할인 전 원가']),
            'rating': '',  # 원본에 없으므로 빈 문자열로 설정
            'product_img': item['상품 이미지']
        }
        transformed_data.append(new_item)
    
    # 새로운 JSON 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=4)
    
    print(f'✅ 변환 완료!')
    print(f'📁 파일 위치: {output_file}')
    print(f'📊 총 {len(transformed_data)}개의 상품 데이터 변환됨')
    
    # 변환된 파일의 첫 번째 항목 출력
    print(f'\n📋 변환 결과 예시:')
    print(json.dumps(transformed_data[0], ensure_ascii=False, indent=2))
    
except FileNotFoundError as e:
    print(f'❌ 파일을 찾을 수 없습니다: {e}')
except Exception as e:
    print(f'❌ 오류 발생: {e}')