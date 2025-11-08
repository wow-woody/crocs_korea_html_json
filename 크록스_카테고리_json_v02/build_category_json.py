import json
import os
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(BASE_DIR, '지비츠_참')

FILES = [
    ('지비츠_참-신상', '지비츠_참-신상_v02.json', '신상'),
    ('지비츠_참-싱글', '지비츠_참-싱글_v02.json', '싱글'),
    ('지비츠_참-팩', '지비츠_참-팩_v02.json', '팩'),
    ('지비츠_참-all', '지비츠_참-all_v02.json', '전체'),
]

OUTPUT_FILE = os.path.join(BASE_DIR, '지비츠_참-카테고리.json')

EXPECTED_KEYS = [
    'id', 'product', 'price', 'price_dc_rate', 'price_cost', 'rating', 'product_img', 'product_img_url', 'category'
]


def normalize_item(raw: Dict[str, Any], category: str) -> Dict[str, Any]:
    """하나의 아이템을 표준 스키마로 정규화합니다."""
    if not isinstance(raw, dict) or not raw:
        return {}

    # 필수 식별자 없으면 제거
    if 'id' not in raw or 'product' not in raw:
        # 일부 파일에서 id가 문자열로 되어 있음 (이미 변환 완료 상태)
        return {}

    item = {
        'id': str(raw.get('id', '')).strip(),
        'product': str(raw.get('product', '')).strip(),
        'price': str(raw.get('price', '')).strip(),
        'price_dc_rate': str(raw.get('price_dc_rate', '')).strip(),
        'price_cost': str(raw.get('price_cost', '')).strip(),
        'rating': str(raw.get('rating', '')).strip(),  # 없으면 빈 문자열
        'product_img': raw.get('product_img') if isinstance(raw.get('product_img'), list) else [],
        'product_img_url': raw.get('product_img_url') if isinstance(raw.get('product_img_url'), list) else [],
        'category': category
    }

    # 가격 및 숫자 필드의 화폐 기호가 혹시 남아있다면 추가 정리
    for price_key in ['price', 'price_dc_rate', 'price_cost']:
        cleaned = item[price_key]
        if isinstance(cleaned, str):
            cleaned = cleaned.replace('₩', '').replace('원', '').replace(',', '').strip()
            item[price_key] = cleaned

    return item


def load_items(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except Exception as e:
        print(f'로드 실패: {path} -> {e}')
        return []


def main():
    merged: List[Dict[str, Any]] = []
    for folder, filename, category in FILES:
        full_path = os.path.join(SOURCE_DIR, folder, filename)
        items = load_items(full_path)
        count_before = len(items)
        normalized = [normalize_item(it, category) for it in items]
        # 빈 객체 제거
        normalized = [n for n in normalized if n.get('id') and n.get('product')]
        print(f'{filename}: {count_before}개 -> 유효 {len(normalized)}개')
        merged.extend(normalized)

    # 최종 결과 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f'병합 완료: {OUTPUT_FILE}')
    print(f'총 {len(merged)}개 항목')

    # 스키마 검증 (간단)
    missing_keys_total = set()
    for it in merged:
        missing = [k for k in EXPECTED_KEYS if k not in it]
        if missing:
            missing_keys_total.update(missing)
    if missing_keys_total:
        print(f'경고: 누락 키 감지 -> {missing_keys_total}')
    else:
        print('모든 항목 스키마 키 포함')

if __name__ == '__main__':
    main()
