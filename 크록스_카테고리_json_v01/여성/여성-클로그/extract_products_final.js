const fs = require('fs');

// HTML 파일 읽기
const htmlContent = fs.readFileSync('여성-클로그_1.html', 'utf-8');

// .ok-card-list 내부의 전체 내용을 찾기
const cardListMatch = htmlContent.match(/<ul class=" ok-card-list">(.*?)<\/ul>/s);
if (!cardListMatch) {
    console.log('ok-card-list를 찾을 수 없습니다.');
    process.exit(1);
}

const cardListContent = cardListMatch[1];

// 각 li 요소를 찾기 (ok-card가 있는 것만)
const liMatches = [...cardListContent.matchAll(/<li[^>]*>(.*?)<\/li>/gs)];

const products = [];
let productIndex = 1;

liMatches.forEach((liMatch, index) => {
    const liContent = liMatch[1];
    
    // ok-card가 있는지 확인
    const cardMatch = liContent.match(/<div class="ok-card"[^>]*data-pidmaster="([^"]+)"[^>]*>(.*?)(?:<\/div>\s*(?:<div class="ok-card__promo"|$))/s);
    
    if (cardMatch) {
        const productId = cardMatch[1];
        const cardContent = cardMatch[2];
        
        try {
            // 상품명 추출
            const nameMatch = cardContent.match(/<div class="ok-card__product-name"[^>]*>([^<]+)<\/div>/);
            const productName = nameMatch ? nameMatch[1].trim() : '';
            
            // 색상 정보 추출
            const colors = [];
            const swatchesMatch = cardContent.match(/<ul class="ok-card__swatches--list[^"]*"[^>]*>(.*?)<\/ul>/s);
            if (swatchesMatch) {
                const colorMatches = [...swatchesMatch[1].matchAll(/<li class="ok-card__swatch-color"[^>]*style="background:\s*rgb\(([^)]+)\);?"[^>]*>/g)];
                colorMatches.forEach(colorMatch => {
                    colors.push(`rgb(${colorMatch[1]})`);
                });
            }
            
            // 가격 정보 추출
            let regularPrice = '';
            let salePrice = '';
            let originalPrice = '';
            let priceRange = '';
            let salePriceOnly = '';
            
            // 가격 섹션 전체 찾기
            const priceMatch = cardContent.match(/<div class="ok-card__price">(.*?)<\/div>/s);
            if (priceMatch) {
                const priceContent = priceMatch[1];
                
                // 할인가 (sale) 찾기
                const saleMatches = [...priceContent.matchAll(/<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]+)<\/span>/g)];
                if (saleMatches.length > 0) {
                    salePrice = saleMatches[0][1].trim();
                    // 할인가-2 (할인율 제거)
                    salePriceOnly = salePrice.replace(/\s*\([^)]+\)/, '').trim();
                }
                
                // 일반 가격 (bold이지만 sale이 아닌 것)
                const boldMatches = [...priceContent.matchAll(/<span[^>]*class="[^"]*ok-card__price-value--bold[^"]*"[^>]*>([^<]+)<\/span>/g)];
                boldMatches.forEach(match => {
                    const spanContent = match[0];
                    if (!spanContent.includes('sale')) {
                        regularPrice = match[1].trim();
                    }
                });
                
                // 할인 전 원가 (discounted)
                const discountedMatch = priceContent.match(/<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>[^₩]*(₩[^<]+)<\/span>/);
                if (discountedMatch) {
                    originalPrice = discountedMatch[1].trim();
                }
                
                // 가격 범위 (~)
                const rangeMatch = priceContent.match(/<span class="ok-card__price-to">\s*~\s*<\/span>(₩[^<]+)<\/span>/);
                if (rangeMatch) {
                    priceRange = `~ ${rangeMatch[1].trim()}`;
                }
            }
            
            // 별점 정보
            let starRating = '';
            const ratingMatch = cardContent.match(/style="width:\s*(\d+)%"[^>]*><span[^>]*>[^<]*out of 5 stars/);
            if (ratingMatch) {
                starRating = 'images/icon_start.svg';
            }
            
            // 리뷰수 추출
            const reviewMatch = cardContent.match(/<div class="ok-star-ratings__ratings-reviewcount">[^(]*\((\d+)\)/);
            const reviewCount = reviewMatch ? reviewMatch[1] : '';
            
            // 카테고리 (.ok-card__snipe > span의 텍스트)
            let category = '';
            const snipeMatch = cardContent.match(/<div class="ok-card__snipe"><span[^>]*>([^<]+)<\/span>/);
            if (snipeMatch) {
                category = snipeMatch[1].trim();
            }
            
            // 상품 이미지 (.ok-card__image-wrap 내의 모든 img src)
            const imageUrls = [];
            const imageWrapMatch = cardContent.match(/<div class="ok-card__image-wrap">(.*?)<\/div>/s);
            if (imageWrapMatch) {
                const imgMatches = [...imageWrapMatch[1].matchAll(/<img[^>]*src="([^"]+)"/g)];
                imgMatches.forEach(imgMatch => {
                    imageUrls.push(imgMatch[1]);
                });
            }
            
            // 상품 데이터 구성
            const product = {
                '번호': productIndex,
                '상품 ID': productId,
                '상품명': productName,
                '색상': colors,
                '가격': regularPrice,
                '할인가 할인율': salePrice,
                '할인~': priceRange,
                '할인가-2': salePriceOnly,
                '할인 전 원가': originalPrice,
                '별점 이미지': starRating,
                '리뷰수': reviewCount,
                '카테고리': category,
                '상품 이미지': imageUrls
            };
            
            products.push(product);
            productIndex++;
            
        } catch (error) {
            console.log(`상품 처리 중 오류 (li ${index + 1}):`, error.message);
        }
    }
});

// JSON 파일로 저장 (예시 파일과 동일한 들여쓰기 사용)
fs.writeFileSync('여성-클로그_2.json', JSON.stringify(products, null, 4), 'utf-8');

console.log(`총 ${products.length}개의 상품이 추출되어 여성-클로그_2.json 파일에 저장되었습니다.`);

// 처음 3개 상품 미리보기
for (let i = 0; i < Math.min(3, products.length); i++) {
    const product = products[i];
    console.log(`\n=== 상품 ${i + 1} ===`);
    console.log(`상품명: ${product['상품명']}`);
    console.log(`상품 ID: ${product['상품 ID']}`);
    console.log(`색상 개수: ${product['색상'].length}개`);
    if (product['색상'].length > 0) {
        console.log(`색상 예시: ${product['색상'].slice(0, 3).join(', ')}...`);
    }
    console.log(`가격: ${product['가격']}`);
    console.log(`할인가: ${product['할인가 할인율']}`);
    console.log(`할인가-2: ${product['할인가-2']}`);
    console.log(`할인 전 원가: ${product['할인 전 원가']}`);
    console.log(`카테고리: ${product['카테고리']}`);
    console.log(`리뷰수: ${product['리뷰수']}`);
    console.log(`이미지 개수: ${product['상품 이미지'].length}개`);
}