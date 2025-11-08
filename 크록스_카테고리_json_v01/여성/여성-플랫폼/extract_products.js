const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// HTML 파일 읽기
const htmlFilePath = path.join(__dirname, '여성-플랫폼.html');
const htmlContent = fs.readFileSync(htmlFilePath, 'utf-8');

// Cheerio로 HTML 파싱
const $ = cheerio.load(htmlContent);

const products = [];
let productNumber = 1;

// .ok-card-list의 모든 li 요소를 순회
$('.ok-card-list li').each((index, element) => {
    const $li = $(element);
    
    // .ok-card가 있는 li만 처리 (빈 li는 제외)
    const $card = $li.find('.ok-card');
    if ($card.length === 0) return;
    
    // 상품 ID 추출
    const productId = $card.attr('data-pidmaster') || '';
    
    // 상품명 추출
    const productName = $card.find('.ok-card__product-name').text().trim() || '';
    
    // 색상 추출 (RGB 색상 배열)
    const colors = [];
    $card.find('.ok-card__swatches--list .ok-card__swatch-color').each((i, colorEl) => {
        const style = $(colorEl).attr('style');
        if (style && style.includes('background:')) {
            const rgbMatch = style.match(/rgb\([^)]+\)/);
            if (rgbMatch) {
                colors.push(rgbMatch[0]);
            }
        }
    });
    
    // 가격 정보 추출
    const $priceSection = $card.find('.ok-card__price');
    let price = '';
    let salePrice = '';
    let discountRange = '';
    let salePrice2 = '';
    let originalPrice = '';
    
    // 기본 가격
    const $priceValue = $priceSection.find('.ok-card__price-value.ok-card__price-value--bold');
    if ($priceValue.length > 0 && !$priceValue.hasClass('ok-card__price-value--sale')) {
        price = $priceValue.text().trim();
    }
    
    // 할인가
    const $saleValue = $priceSection.find('.ok-card__price-value.ok-card__price-value--bold.ok-card__price-value--sale');
    if ($saleValue.length > 0) {
        salePrice = $saleValue.text().trim();
    }
    
    // 할인 범위 (~)
    const $priceTo = $priceSection.find('.ok-card__price-to');
    if ($priceTo.length > 0) {
        discountRange = $priceTo.text().trim();
    }
    
    // 할인가-2 (일반 price-value)
    const $regularPrice = $priceSection.find('.ok-card__price-value').not('.ok-card__price-value--bold, .ok-card__price-value--discounted, .ok-card__price-value--sale');
    if ($regularPrice.length > 0) {
        salePrice2 = $regularPrice.text().trim();
    }
    
    // 할인 전 원가
    const $originalPriceEl = $priceSection.find('.ok-card__price-value.ok-card__price-value--discounted');
    if ($originalPriceEl.length > 0) {
        originalPrice = $originalPriceEl.text().trim();
    }
    
    // 리뷰수 추출
    const reviewCount = $card.find('.ok-star-ratings__ratings-reviewcount').text().trim() || '';
    
    // 카테고리 추출
    const category = $card.find('.ok-card__snipe > span').text().trim() || '';
    
    // 상품 이미지 추출
    const images = [];
    $card.find('.ok-card__image-wrap img').each((i, imgEl) => {
        const src = $(imgEl).attr('src');
        if (src) {
            images.push(src);
        }
    });
    
    // 상품 정보가 유효한 경우에만 추가
    if (productId || productName || images.length > 0) {
        products.push({
            "번호": productNumber++,
            "상품 ID": productId,
            "상품명": productName,
            "색상": colors,
            "가격": price,
            "할인가 할인율": salePrice,
            "할인~": discountRange,
            "할인가-2": salePrice2,
            "할인 전 원가": originalPrice,
            "별점 이미지": "./images/icon_start.svg",
            "리뷰수": reviewCount,
            "카테고리": category,
            "상품 이미지": images
        });
    }
});

// JSON 파일로 저장
const outputPath = path.join(__dirname, '여성-플랫폼.json');
fs.writeFileSync(outputPath, JSON.stringify(products, null, 2), 'utf-8');

console.log(`총 ${products.length}개의 상품이 추출되었습니다.`);
console.log(`JSON 파일이 생성되었습니다: ${outputPath}`);