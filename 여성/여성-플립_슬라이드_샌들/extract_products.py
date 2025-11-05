import json
import re
from bs4 import BeautifulSoup

def extract_product_data(html_file):
    """HTML 파일에서 상품 데이터를 추출하여 JSON 형태로 변환"""
    
    # HTML 파일 읽기
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ok-card-list 내의 모든 li 태그 찾기
    card_list = soup.find('ul', class_='ok-card-list')
    if not card_list:
        print("ok-card-list를 찾을 수 없습니다.")
        return []
    
    # 모든 li 태그 중 ok-card가 있는 것들만 필터링
    li_elements = card_list.find_all('li')
    product_cards = [li for li in li_elements if li.find('div', class_='ok-card')]
    
    products = []
    
    for idx, li in enumerate(product_cards, 1):
        ok_card = li.find('div', class_='ok-card')
        if not ok_card:
            continue
            
        product = {}
        product["번호"] = idx
        
        # 상품 ID (data-pidmaster)
        product["상품 ID"] = ok_card.get('data-pidmaster', '')
        
        # 상품명
        product_name_elem = ok_card.find('div', class_='ok-card__product-name')
        product["상품명"] = product_name_elem.get_text(strip=True) if product_name_elem else ''
        
        # 색상 정보 추출
        colors = []
        swatch_list = ok_card.find('ul', class_='ok-card__swatches--list')
        if swatch_list:
            swatch_colors = swatch_list.find_all('li', class_='ok-card__swatch-color')
            for swatch in swatch_colors:
                style = swatch.get('style', '')
                if 'background:' in style:
                    colors.append(style.strip())
        product["색상"] = colors
        
        # 가격 정보 추출
        price_section = ok_card.find('div', class_='ok-card__price')
        
        # 가격 정보 초기화
        product["가격"] = ''
        product["할인가 할인율"] = ''
        product["할인~"] = ''
        product["할인가-2"] = ''
        product["할인 전 원가"] = ''
        
        if price_section:
            # 할인가 할인율 (ok-card__price-value--sale)
            sale_price_elem = price_section.find('span', class_='ok-card__price-value--sale')
            if sale_price_elem:
                sale_text = sale_price_elem.get_text(strip=True)
                # 불필요한 문자 제거
                sale_text = re.sub(r'\s+', ' ', sale_text)
                product["할인가 할인율"] = sale_text
            
            # 할인~ (ok-card__price-to)
            price_to_elem = price_section.find('span', class_='ok-card__price-to')
            if price_to_elem:
                product["할인~"] = price_to_elem.get_text(strip=True)
            
            # 할인 전 원가 (ok-card__price-value--discounted)
            discounted_price_elem = price_section.find('span', class_='ok-card__price-value--discounted')
            if discounted_price_elem:
                discounted_text = discounted_price_elem.get_text(strip=True)
                # ";undefined" 제거
                discounted_text = discounted_text.replace(';undefined', '')
                product["할인 전 원가"] = discounted_text
            
            # 가격 범위가 있는 경우 처리 (₩24,900 ~ ₩37,900 같은 형태)
            price_range_spans = price_section.find_all('span', class_='ok-card__price-value--sale')
            if len(price_range_spans) > 1:
                # 두 번째 span에 가격 범위가 있는 경우
                second_span = price_range_spans[1]
                range_text = second_span.get_text(strip=True)
                if '₩' in range_text and product["할인~"]:
                    product["할인가-2"] = range_text
            
            # 일반 가격 (ok-card__price-value but not sale or discounted)
            price_values = price_section.find_all('span', class_='ok-card__price-value')
            for pv in price_values:
                classes = pv.get('class', [])
                # sale이나 discounted 클래스가 없는 경우
                if 'ok-card__price-value--sale' not in classes and 'ok-card__price-value--discounted' not in classes:
                    text = pv.get_text(strip=True)
                    if text and '₩' in text:
                        product["가격"] = text
                        break
        
        # 별점 이미지 (고정값)
        product["별점 이미지"] = "./images/icon_start.svg"
        
        # 리뷰수
        review_count_elem = ok_card.find('div', class_='ok-star-ratings__ratings-reviewcount')
        if review_count_elem:
            review_text = review_count_elem.get_text(strip=True)
            # 숫자만 추출 (괄호와 "평점;" 제거)
            review_match = re.search(r'\((\d+)\)', review_text)
            product["리뷰수"] = review_match.group(1) if review_match else ''
        else:
            product["리뷰수"] = ''
        
        # 카테고리
        snipe_elem = ok_card.find('div', class_='ok-card__snipe')
        if snipe_elem:
            span_elem = snipe_elem.find('span')
            if span_elem:
                category_text = span_elem.get_text(strip=True)
                # 줄바꿈 및 여분의 공백 제거
                category_text = re.sub(r'\s+', ' ', category_text)
                product["카테고리"] = category_text
            else:
                product["카테고리"] = ''
        else:
            product["카테고리"] = ''
        
        # 상품 이미지들
        image_wrap = ok_card.find('div', class_='ok-card__image-wrap')
        images = []
        if image_wrap:
            img_tags = image_wrap.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if src:
                    images.append(src)
        product["상품 이미지"] = images
        
        products.append(product)
        
        print(f"상품 {idx} 처리 완료: {product['상품명']}")
    
    return products

def save_to_json(products, output_file):
    """상품 데이터를 JSON 파일로 저장"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"JSON 파일이 저장되었습니다: {output_file}")

if __name__ == "__main__":
    # HTML 파일 경로
    html_file = "여성-플립_슬라이드.html"
    
    # 출력 JSON 파일 경로
    output_file = "여성-플립_슬라이드.json"
    
    print("HTML 파일에서 상품 데이터 추출 시작...")
    
    try:
        # 상품 데이터 추출
        products = extract_product_data(html_file)
        
        if products:
            print(f"총 {len(products)}개의 상품을 추출했습니다.")
            
            # JSON 파일로 저장
            save_to_json(products, output_file)
            
            # 샘플 출력
            print("\n첫 번째 상품 예시:")
            print(json.dumps(products[0], ensure_ascii=False, indent=2))
            
        else:
            print("추출된 상품이 없습니다.")
            
    except FileNotFoundError:
        print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")