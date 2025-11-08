import json
import re

def transform_json_file(input_path, output_path):
    """
    JSON 파일을 변환하여 React에서 사용할 수 있는 형태로 만듭니다.
    
    변환 규칙:
    - "번호" 필드 삭제
    - "상품 ID" -> "id"
    - "상품명" -> "product"
    - "가격" -> "price"
    - "할인가 할인율" -> "price_dc_rate"
    - "할인 전 원가" -> "price_cost"
    - "별점 이미지" -> "rating"
    - "상품 이미지" -> "product_img"
    - 가격에서 "₩" 및 "원" 표시 제거
    """
    
    try:
        print(f"파일 읽는 중: {input_path}")
        
        # JSON 파일 읽기
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"총 {len(data)}개 항목을 읽었습니다.")
        
        # 데이터 변환
        transformed_data = []
        
        for item in data:
            new_item = {}
            
            # 필드명 변경 및 번호 필드 제거
            for key, value in item.items():
                if key == "번호":
                    continue  # 번호 필드 삭제
                elif key == "상품 ID" or key == "상품_ID":
                    new_item["id"] = value
                elif key == "상품명" or key == "상품명 ":
                    new_item["product"] = value
                elif key == "가격":
                    # 가격에서 ₩ 및 원화 표시 제거
                    if isinstance(value, str):
                        clean_price = re.sub(r'[₩원,]', '', value).strip()
                        new_item["price"] = clean_price
                    else:
                        new_item["price"] = value
                elif key == "할인가 할인율" or key == "할인가_할인율":
                    if isinstance(value, str):
                        clean_value = re.sub(r'[₩원,]', '', value).strip()
                        new_item["price_dc_rate"] = clean_value
                    else:
                        new_item["price_dc_rate"] = value
                elif key == "할인 전 원가" or key == "할인_전_원가":
                    if isinstance(value, str):
                        clean_value = re.sub(r'[₩원,]', '', value).strip()
                        new_item["price_cost"] = clean_value
                    else:
                        new_item["price_cost"] = value
                elif key == "별점 이미지":
                    new_item["rating"] = value
                elif key == "상품 이미지" or key == "상품_이미지":
                    new_item["product_img"] = value
                else:
                    # 다른 필드는 그대로 유지 (상품_이미지_원본 등)
                    new_item[key] = value
            
            transformed_data.append(new_item)
        
        # 변환된 데이터를 새 파일에 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, ensure_ascii=False, indent=2)
        
        print(f"변환 완료: {output_path}")
        print(f"총 {len(transformed_data)}개 항목이 변환되었습니다.")
        
    except FileNotFoundError:
        print(f"오류: {input_path} 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")

# 실행
if __name__ == "__main__":
    input_file = "지비츠_참-all/지비츠_참-all.json"
    output_file = "지비츠_참-all/지비츠_참-all_v02.json"
    
    transform_json_file(input_file, output_file)