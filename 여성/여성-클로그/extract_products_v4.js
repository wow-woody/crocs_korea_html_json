const fs = require('fs');
const { JSDOM } = require('jsdom');

// RGB 색상 추출 함수
function extractRgbColor(styleText) {
    if (!styleText) return "";
    
    // rgb(숫자, 숫자, 숫자) 패턴 찾기
    const rgbMatch = styleText.match(/rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/);
    if (rgbMatch) {
        return `rgb(${rgbMatch[1]}, ${rgbMatch[2]}, ${rgbMatch[3]})`;
    }
    return "";
}

// HTML에서 상품 정보 추출
function extractProductsFromHtml(htmlFilePath) {
    // HTML 파일 읽기
    const htmlContent = fs.readFileSync(htmlFilePath, 'utf-8');
    const dom = new JSDOM(htmlContent);
    const document = dom.window.document;
    
    // .ok-card-list 내의 모든 li 요소 찾기
    const cardList = document.querySelector('ul.ok-card-list');
    if (!cardList) {
        console.log("ok-card-list를 찾을 수 없습니다.");
        return [];
    }
    
    const liElements = cardList.querySelectorAll('li');
    const products = [];
    
    // 번호는 69부터 시작
    let counter = 69;
    
    liElements.forEach(li => {
        // .ok-card가 있는 li만 처리
        const cardDiv = li.querySelector('div.ok-card');
        if (!cardDiv) return;
        
        const product = {};
        
        // 번호
        product["번호"] = counter++;
        
        // 상품 ID (data-pidmaster 속성)
        const productId = cardDiv.getAttribute('data-pidmaster') || '';
        product["상품 ID"] = productId;
        
        // 상품명 (.ok-card__product-name)
        const productNameElem = cardDiv.querySelector('div.ok-card__product-name');
        const productName = productNameElem ? productNameElem.textContent.trim() : '';
        product["상품명"] = productName;
        
        // 색상 (.ok-card__swatches--list 내의 .ok-card__swatch-color의 style 속성)
        const colors = [];
        const swatchesList = cardDiv.querySelector('div.ok-card__swatches--list');
        if (swatchesList) {
            const swatchColors = swatchesList.querySelectorAll('div.ok-card__swatch-color');
            swatchColors.forEach(swatch => {
                const style = swatch.getAttribute('style') || '';
                const rgbColor = extractRgbColor(style);
                if (rgbColor) {
                    colors.push(rgbColor);
                }
            });
        }
        product["색상"] = colors;
        
        // 가격 정보들
        const priceSection = cardDiv.querySelector('div.ok-card__price');
        
        // 가격 (.ok-card__price-value.ok-card__price-value--bold)
        let priceBold = "";
        if (priceSection) {
            const priceBoldElem = priceSection.querySelector('span.ok-card__price-value.ok-card__price-value--bold:not(.ok-card__price-value--sale)');
            if (priceBoldElem) {
                priceBold = priceBoldElem.textContent.trim();
            }
        }
        product["가격"] = priceBold;
        
        // 할인가 할인율 (.ok-card__price-value--sale)
        let salePrice = "";
        if (priceSection) {
            const salePriceElem = priceSection.querySelector('span.ok-card__price-value--sale');
            if (salePriceElem) {
                salePrice = salePriceElem.textContent.trim();
            }
        }
        product["할인가 할인율"] = salePrice;
        
        // 할인~ (.ok-card__price-to)
        let priceTo = "";
        if (priceSection) {
            const priceToElem = priceSection.querySelector('.ok-card__price-to');
            if (priceToElem) {
                priceTo = priceToElem.textContent.trim();
            }
        }
        product["할인~"] = priceTo;
        
        // 할인가-2 (.ok-card__price-value 가격 텍스트) - sale이 아닌 일반 price-value
        let priceValue = "";
        if (priceSection) {
            const priceValues = priceSection.querySelectorAll('span.ok-card__price-value:not(.ok-card__price-value--bold):not(.ok-card__price-value--sale):not(.ok-card__price-value--discounted)');
            if (priceValues.length > 0) {
                priceValue = priceValues[0].textContent.trim();
            }
        }
        product["할인가-2"] = priceValue;
        
        // 할인 전 원가 (.ok-card__price-value--discounted)
        let discountedPrice = "";
        if (priceSection) {
            const discountedElem = priceSection.querySelector('span.ok-card__price-value--discounted');
            if (discountedElem) {
                discountedPrice = discountedElem.textContent.trim();
            }
        }
        product["할인 전 원가"] = discountedPrice;
        
        // 별점 이미지 (고정값)
        product["별점 이미지"] = "./images/icon_start.svg";
        
        // 리뷰수 (.ok-star-ratings__ratings-reviewcount)
        let reviewCount = "";
        const reviewElem = cardDiv.querySelector('.ok-star-ratings__ratings-reviewcount');
        if (reviewElem) {
            reviewCount = reviewElem.textContent.trim();
        }
        product["리뷰수"] = reviewCount;
        
        // 카테고리 (.ok-card__snipe > span)
        let category = "";
        const snipeElem = cardDiv.querySelector('div.ok-card__snipe');
        if (snipeElem) {
            const spanElem = snipeElem.querySelector('span');
            if (spanElem) {
                category = spanElem.textContent.trim();
            }
        }
        product["카테고리"] = category;
        
        // 상품 이미지 (.ok-card__image-wrap img의 모든 src)
        const imageUrls = [];
        const imageWrap = cardDiv.querySelector('div.ok-card__image-wrap');
        if (imageWrap) {
            const imgTags = imageWrap.querySelectorAll('img');
            imgTags.forEach(img => {
                const src = img.getAttribute('src');
                if (src) {
                    imageUrls.push(src);
                }
            });
        }
        product["상품 이미지"] = imageUrls;
        
        products.push(product);
    });
    
    return products;
}

// 메인 함수
function main() {
    const htmlFile = "여성-클로그_2.html";
    
    if (!fs.existsSync(htmlFile)) {
        console.log(`파일을 찾을 수 없습니다: ${htmlFile}`);
        return;
    }
    
    console.log(`HTML 파일에서 상품 정보를 추출 중: ${htmlFile}`);
    
    // 상품 정보 추출
    const products = extractProductsFromHtml(htmlFile);
    
    if (products.length === 0) {
        console.log("추출된 상품이 없습니다.");
        return;
    }
    
    console.log(`총 ${products.length}개의 상품을 추출했습니다.`);
    
    // JSON 파일로 저장
    const outputFile = "여성-클로그_2.json";
    
    fs.writeFileSync(outputFile, JSON.stringify(products, null, 2), 'utf-8');
    
    console.log(`JSON 파일이 생성되었습니다: ${outputFile}`);
    
    // 첫 번째 상품 정보 출력 (확인용)
    if (products.length > 0) {
        console.log("\n첫 번째 상품 정보:");
        console.log(JSON.stringify(products[0], null, 2));
    }
}

// 실행
main();