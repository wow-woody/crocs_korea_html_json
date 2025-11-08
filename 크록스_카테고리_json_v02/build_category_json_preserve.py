import json
import os
from typing import Any

BASE_DIR = os.path.dirname(__file__)
SRC = os.path.join(BASE_DIR, '지비츠_참')

SOURCES = [
    ('지비츠_참-신상_v02', os.path.join(SRC, '지비츠_참-신상', '지비츠_참-신상_v02.json')),
    ('지비츠_참-싱글_v02', os.path.join(SRC, '지비츠_참-싱글', '지비츠_참-싱글_v02.json')),
    ('지비츠_참-팩_v02',   os.path.join(SRC, '지비츠_참-팩',   '지비츠_참-팩_v02.json')),
    ('지비츠_참-all_v02',  os.path.join(SRC, '지비츠_참-all',  '지비츠_참-all_v02.json')),
]

OUT_PATH = os.path.join(BASE_DIR, '지비츠_참-카테고리.json')

def load_as_is(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    result = {}
    for key, path in SOURCES:
        data = load_as_is(path)
        result[key] = data
        print(f"{key}: {len(data) if isinstance(data, list) else 'object'} 항목")

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {OUT_PATH}")

if __name__ == '__main__':
    main()
