import os
import json
import shutil

def rename_image_files():
    """images 폴더 내의 파일명에서 공백을 "_"로 대체"""
    
    images_dir = "images"
    if not os.path.exists(images_dir):
        print("images 폴더가 존재하지 않습니다.")
        return {}
    
    # 파일명 변경 매핑 저장
    rename_mapping = {}
    
    # 폴더 내 모든 파일 확인
    files = os.listdir(images_dir)
    jpg_files = [f for f in files if f.endswith('.jpg')]
    
    print(f"총 {len(jpg_files)}개의 이미지 파일을 확인합니다...\n")
    
    for filename in jpg_files:
        # 공백이 포함된 파일명만 처리
        if ' ' in filename:
            new_filename = filename.replace(' ', '_')
            
            old_path = os.path.join(images_dir, filename)
            new_path = os.path.join(images_dir, new_filename)
            
            try:
                # 파일명 변경
                os.rename(old_path, new_path)
                
                # 매핑 저장 (JSON 업데이트용)
                old_relative_path = f"./images/{filename}"
                new_relative_path = f"./images/{new_filename}"
                rename_mapping[old_relative_path] = new_relative_path
                
                print(f"✅ 변경 완료: {filename} → {new_filename}")
                
            except Exception as e:
                print(f"❌ 변경 실패: {filename} - {e}")
        else:
            print(f"⏭️  변경 불필요: {filename}")
    
    if rename_mapping:
        print(f"\n📊 총 {len(rename_mapping)}개 파일명이 변경되었습니다.")
    else:
        print("\n✅ 변경이 필요한 파일이 없습니다.")
    
    return rename_mapping

def update_json_files(rename_mapping):
    """JSON 파일들의 이미지 경로 업데이트"""
    
    json_files = ["여성-플립_슬라이드.json", "여성-샌들.json"]
    
    for json_file in json_files:
        if not os.path.exists(json_file):
            print(f"⚠️  파일이 존재하지 않습니다: {json_file}")
            continue
        
        try:
            # JSON 파일 읽기
            with open(json_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            updated_count = 0
            
            # 각 상품의 이미지 경로 업데이트
            for product in products:
                images = product.get("상품 이미지", [])
                updated_images = []
                
                for img_path in images:
                    if img_path in rename_mapping:
                        updated_images.append(rename_mapping[img_path])
                        updated_count += 1
                    else:
                        updated_images.append(img_path)
                
                product["상품 이미지"] = updated_images
            
            # 업데이트된 JSON 저장
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {json_file}: {updated_count}개 이미지 경로 업데이트 완료")
            
        except Exception as e:
            print(f"❌ {json_file} 업데이트 실패: {e}")

def main():
    print("🔄 images 폴더 파일명 공백 제거 작업 시작...\n")
    
    # 1. 파일명 변경
    rename_mapping = rename_image_files()
    
    # 2. JSON 파일 업데이트 (변경된 파일이 있는 경우에만)
    if rename_mapping:
        print(f"\n📝 JSON 파일들의 이미지 경로를 업데이트합니다...")
        update_json_files(rename_mapping)
        
        print(f"\n🎉 모든 작업이 완료되었습니다!")
        print(f"   - 파일명 변경: {len(rename_mapping)}개")
        print(f"   - JSON 업데이트: 2개 파일")
    else:
        print(f"\n✅ 이미 모든 파일명이 올바른 형식입니다!")

if __name__ == "__main__":
    main()