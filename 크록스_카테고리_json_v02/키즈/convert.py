import os
import json

# 병합할 JSON 파일 경로
folder_path = r"C:\Users\jjeon\OneDrive\김정우\크록스\02-상품리스트-js파일\크록스_카테고리_json_v02\키즈"
file_names = [
    "키즈-부츠_레인부츠_v02.json",
    "키즈-샌들_v02.json",
    "키즈-클로그_v02.json"
]

# 병합된 데이터를 저장할 리스트
merged_data = []

# 각 파일을 읽고 병합
for file_name in file_names:
    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                print(f"⚠️ 리스트 형식이 아닌 JSON: {file_name}")
    except Exception as e:
        print(f"❌ 오류 발생: {file_name} - {e}")

# 병합된 결과 저장
output_file = os.path.join(folder_path, "키즈-카테고리.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print(f"✅ 병합 완료: {output_file}")
