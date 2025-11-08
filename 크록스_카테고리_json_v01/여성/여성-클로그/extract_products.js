const fs = require('fs');

// HTML 파일 읽기
const htmlContent = fs.readFileSync('여성-클로그_1.html', 'utf-8');

// 상품 카드들을 찾는 정규식
const productCardRegex = /<div class="ok-card"[^>]*data-pidmaster="([^"]+)"[^>]*>(.*?)<\/div>\s*(?=<div class="ok-card__promo")/gs;

const products = [];
let match;
let index = 1;

while ((match = productCardRegex.exec(htmlContent)) !== null) {
    const productId = match[1];
    const cardContent = match[2];
    
    try {
        // 상품명 추출
        const nameMatch = cardContent.match(/<div class="ok-card__product-name"[^>]*>([^<]+)<\/div>/);
        const productName = nameMatch ? nameMatch[1].trim() : '';
        
        // 색상 정보 추출
        const colors = [];
        const colorMatches = cardContent.match(/style="background:\s*([^"]+)"/g) || [];
        
        colorMatches.forEach(colorMatch => {
            const colorStyle = colorMatch.match(/background:\s*([^"]+)/)[1];
            if (colorStyle.includes('rgb(')) {
                const rgbMatches = colorStyle.match(/rgb\((\d+,\s*\d+,\s*\d+)\)/g) || [];
                rgbMatches.forEach(rgb => colors.push(rgb));
            } else if (colorStyle.includes('linear-gradient')) {
                colors.push('그라데이션');
            }
        });
        
        if (colors.length === 0) {
            colors.push('색상정보없음');
        }
        
        // 가격 정보 추출
        const priceInfo = {};
        
        // 할인가 추출
        const saleMatch = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]+)<\/span>/);
        if (saleMatch) {
            const saleText = saleMatch[1].trim();
            priceInfo['할인가'] = saleText;
            
            // 할인율 추출
            const discountMatch = saleText.match(/\((\d+%)\)/);
            if (discountMatch) {
                priceInfo['할인율'] = discountMatch[1];
                priceInfo['할인가-2'] = saleText.split('(')[0].trim();
            }
        }
        
        // 원가 추출
        const originalMatch = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>(?:[^<]+)?(₩[^<]+)<\/span>/);
        if (originalMatch) {
            priceInfo['할인 전 원가'] = originalMatch[1].trim();
        }
        
        // 일반 가격
        const regularMatch = cardContent.match(/<span[^>]*class="[^"]*ok-card__price-value--bold[^"]*"[^>]*>(₩[^<]+)<\/span>/);
        if (regularMatch && !priceInfo['할인가']) {
            priceInfo['가격'] = regularMatch[1].trim();
        }
        
        // 별점 추출
        const ratingInfo = {};
        const ratingMatch = cardContent.match(/style="width:\s*(\d+)%"[^>]*><span[^>]*>([^<]+) out of 5 stars/);
        if (ratingMatch) {
            const widthPercent = parseInt(ratingMatch[1]);
            ratingInfo['별점'] = (widthPercent / 20).toFixed(1);
        }
        
        // 리뷰수 추출
        const reviewMatch = cardContent.match(/<div class="ok-star-ratings__ratings-reviewcount">[^(]*\((\d+)\)/);
        if (reviewMatch) {
            ratingInfo['리뷰수'] = reviewMatch[1];
        }
        
        // 상품 이미지 URL 추출
        const imageMatch = cardContent.match(/<img[^>]*src="([^"]+)"/);
        const imageUrl = imageMatch ? imageMatch[1] : '';
        
        // 상품 데이터 구성
        const product = {
            '번호': index,
            '상품 ID': productId,
            '상품명': productName,
            '색상': colors.slice(0, 5), // 최대 5개 색상만
            '가격': priceInfo['가격'] || '',
            '할인가 할인율': priceInfo['할인가'] || '',
            '할인~': priceInfo['할인~'] || '',
            '할인가-2': priceInfo['할인가-2'] || '',
            '할인 전 원가': priceInfo['할인 전 원가'] || '',
            '별점 이미지': ratingInfo['별점'] || '',
            '리뷰수': ratingInfo['리뷰수'] || '',
            '카테고리': '여성-클로그',
            '상품 이미지': imageUrl
        };
        
        products.push(product);
        index++;
        
    } catch (error) {
        console.log(`상품 ${index} 처리 중 오류:`, error.message);
    }
}

// JSON 파일로 저장
fs.writeFileSync('여성-클로그.json', JSON.stringify(products, null, 2), 'utf-8');

console.log(`총 ${products.length}개의 상품이 추출되어 여성-클로그.json 파일에 저장되었습니다.`);

// 처음 3개 상품 미리보기
for (let i = 0; i < Math.min(3, products.length); i++) {
    console.log(`\n상품 ${i + 1}: ${products[i]['상품명']}`);
    console.log(`  - 상품 ID: ${products[i]['상품 ID']}`);
    console.log(`  - 색상: ${products[i]['색상'].slice(0, 2).join(', ')}...`);
    console.log(`  - 가격정보: ${products[i]['할인가 할인율'] || products[i]['가격']}`);
}