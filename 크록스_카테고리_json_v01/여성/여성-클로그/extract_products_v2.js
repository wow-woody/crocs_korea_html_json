const fs = require('fs');

// HTML 파일 읽기
const htmlContent = fs.readFileSync('여성-클로그_1.html', 'utf-8');

// .ok-card-list 안의 모든 li 요소를 찾기
const liRegex = /<li[^>]*>(.*?)<\/li>/gs;
const products = [];
let index = 1;

let match;
while ((match = liRegex.exec(htmlContent)) !== null) {
    const liContent = match[1];
    
    // .ok-card가 있는 li만 처리
    const cardMatch = liContent.match(/<div class="ok-card"[^>]*data-pidmaster="([^"]+)"[^>]*>(.*?)(?=<\/div>\s*$)/s);
    
    if (cardMatch) {
        const productId = cardMatch[1];
        const cardContent = cardMatch[2];
        
        try {
            // 상품명 추출
            const nameMatch = cardContent.match(/<div class="ok-card__product-name"[^>]*>([^<]+)<\/div>/);
            const productName = nameMatch ? nameMatch[1].trim() : '';
            
            // 색상 정보 추출 (.ok-card__swatches--list li의 style 속성)
            const colors = [];
            const swatchesMatch = cardContent.match(/<ul class="ok-card__swatches--list[^"]*"[^>]*>(.*?)<\/ul>/s);
            if (swatchesMatch) {
                const swatchContent = swatchesMatch[1];
                const colorMatches = swatchContent.match(/<li[^>]*style="background:\s*([^"]+)"[^>]*>/g) || [];
                
                colorMatches.forEach(colorMatch => {
                    const styleMatch = colorMatch.match(/style="background:\s*([^"]+)"/);
                    if (styleMatch) {
                        const colorStyle = styleMatch[1];
                        if (colorStyle.includes('rgb(')) {
                            const rgbMatches = colorStyle.match(/rgb\(([^)]+)\)/g) || [];
                            rgbMatches.forEach(rgb => colors.push(rgb));
                        }
                    }
                });
            }
            
            // 가격 정보 추출
            let regularPrice = '';
            let salePrice = '';
            let originalPrice = '';
            let priceRange = '';
            
            // 일반 가격 (.ok-card__price-value--bold이지만 sale이 아닌 것)
            const regularPriceMatch = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value[^"]*ok-card__price-value--bold[^"]*"[^>]*>(?!.*sale)(₩[^<]+)<\/span>/);
            if (regularPriceMatch) {
                regularPrice = regularPriceMatch[1].trim();
            }
            
            // 할인가 (.ok-card__price-value--sale)
            const saleMatches = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]+)<\/span>/g) || [];
            if (saleMatches.length > 0) {
                salePrice = saleMatches[0].match(/>([^<]+)</)[1].trim();
            }
            
            // 할인 전 원가 (.ok-card__price-value--discounted)
            const originalPriceMatch = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>[^₩]*(₩[^<]+)<\/span>/);
            if (originalPriceMatch) {
                originalPrice = originalPriceMatch[1].trim();
            }
            
            // 할인~ (.ok-card__price-to)
            const priceToMatch = cardContent.match(/<span class="ok-card__price-to">[^<]*~[^<]*<\/span>(₩[^<]+)<\/span>/);
            if (priceToMatch) {
                priceRange = `~ ${priceToMatch[1].trim()}`;
            }
            
            // 별점 정보 (width 퍼센트를 5점 만점으로 계산)
            let starRating = '';
            const ratingMatch = cardContent.match(/style="width:\s*(\d+)%"/);
            if (ratingMatch) {
                const widthPercent = parseInt(ratingMatch[1]);
                const rating = (widthPercent / 20).toFixed(1);
                starRating = 'images/icon_start.svg';
            }
            
            // 리뷰수 추출
            const reviewMatch = cardContent.match(/<div class="ok-star-ratings__ratings-reviewcount">[^(]*\((\d+)\)/);
            const reviewCount = reviewMatch ? reviewMatch[1] : '';
            
            // 카테고리 (.ok-card__snipe > span)
            let category = '';
            const snipeMatch = cardContent.match(/<div class="ok-card__snipe"><span[^>]*>([^<]+)<\/span><\/div>/);
            if (snipeMatch) {
                category = snipeMatch[1].trim();
            }
            
            // 상품 이미지 (.ok-card__image-wrap img의 모든 src)
            const imageUrls = [];
            const imageMatches = cardContent.match(/<div class="ok-card__image-wrap">(.*?)<\/div>/s);
            if (imageMatches) {
                const imageContent = imageMatches[1];
                const imgMatches = imageContent.match(/<img[^>]*src="([^"]+)"/g) || [];
                imgMatches.forEach(imgMatch => {
                    const srcMatch = imgMatch.match(/src="([^"]+)"/);
                    if (srcMatch) {
                        imageUrls.push(srcMatch[1]);
                    }
                });
            }
            
            // 상품 데이터 구성
            const product = {
                '번호': index,
                '상품 ID': productId,
                '상품명': productName,
                '색상': colors,
                '가격': regularPrice,
                '할인가 할인율': salePrice,
                '할인~': priceRange,
                '할인가-2': salePrice.split('(')[0].trim() || salePrice,
                '할인 전 원가': originalPrice,
                '별점 이미지': starRating,
                '리뷰수': reviewCount,
                '카테고리': category,
                '상품 이미지': imageUrls
            };
            
            products.push(product);
            index++;
            
        } catch (error) {
            console.log(`상품 ${index} 처리 중 오류:`, error.message);
        }
    }
}

// JSON 파일로 저장
fs.writeFileSync('여성-클로그_2.json', JSON.stringify(products, null, 4), 'utf-8');

console.log(`총 ${products.length}개의 상품이 추출되어 여성-클로그_2.json 파일에 저장되었습니다.`);

// 처음 3개 상품 미리보기
for (let i = 0; i < Math.min(3, products.length); i++) {
    console.log(`\n상품 ${i + 1}: ${products[i]['상품명']}`);
    console.log(`  - 상품 ID: ${products[i]['상품 ID']}`);
    console.log(`  - 색상 개수: ${products[i]['색상'].length}개`);
    console.log(`  - 가격: ${products[i]['가격'] || products[i]['할인가 할인율']}`);
    console.log(`  - 카테고리: ${products[i]['카테고리']}`);
    console.log(`  - 이미지 개수: ${products[i]['상품 이미지'].length}개`);
}