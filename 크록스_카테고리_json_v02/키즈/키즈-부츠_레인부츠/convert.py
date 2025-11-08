import json
import re

with open('키즈-부츠_레인부츠.json', encoding='utf-8') as f:
    data = json.load(f)

result = []
for item in data:
    new_item = {
        "id": item.get("상품 ID", ""),
        "product": item.get("상품명", ""),
        "color": item.get("색상", []),
        "price": re.sub(r"₩", "", item.get("가격", "")),
        "price_dc_rate": re.sub(r"₩", "", item.get("할인가 할인율", "")),
        "price_~": re.sub(r"₩", "", item.get("할인~", "")),
        "price_dc_2": re.sub(r"₩", "", item.get("할인가-2", "")),
        "price_cost": re.sub(r"₩", "", item.get("할인 전 원가", "")),
        "rating": item.get("별점 이미지", ""),
        "review": re.sub(r"[()]", "", item.get("리뷰수", "")),
        "cate": item.get("카테고리", ""),
        "product_img": item.get("상품 이미지", [])
    }
    result.append(new_item)

with open('키즈-부츠_레인부츠_v02.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)