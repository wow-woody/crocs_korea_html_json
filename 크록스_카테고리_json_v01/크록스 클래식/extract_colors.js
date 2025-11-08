const fs = require('fs');
const cheerio = require('cheerio');

// HTML 파일 읽기
const htmlContent = fs.readFileSync('./신상품&트렌드.html', 'utf8');
const $ = cheerio.load(htmlContent);

// JSON 파일 읽기
const jsonData = JSON.parse(fs.readFileSync('./crocs_products_신상품.json', 'utf8'));

// 각 상품 카드에서 색상 정보 추출
const productCards = $('.ok-card').toArray();

// 상품별 색상 정보 수집
const colorData = [];

productCards.forEach((card, index) => {
    const $card = $(card);
    const productId = $card.attr('data-pidmaster');
    const colors = [];
    
    // 해당 카드의 색상 스와치들 추출
    $card.find('.ok-card__swatch-color').each((i, swatch) => {
        const style = $(swatch).attr('style');
        if (style && style.includes('background:')) {
            const colorMatch = style.match(/background:\s*(rgb\([^)]+\)|#[a-fA-F0-9]+|[a-zA-Z]+)/);
            if (colorMatch) {
                colors.push(colorMatch[1].trim());
            }
        }
    });
    
    colorData.push({
        productId,
        colors,
        index: index
    });
});

// JSON 데이터에 색상 정보 추가
jsonData.products_new.forEach((product, index) => {
    const matchingColor = colorData.find(c => c.productId === product["상품 ID"]);
    
    if (matchingColor && matchingColor.colors.length > 0) {
        // "상품명" 바로 뒤에 "색상" 필드 추가
        const newProduct = {};
        Object.keys(product).forEach(key => {
            newProduct[key] = product[key];
            if (key === "상품명") {
                newProduct["색상"] = matchingColor.colors;
            }
        });
        jsonData.products_new[index] = newProduct;
    } else {
        // 색상이 없는 경우 빈 배열 추가
        const newProduct = {};
        Object.keys(product).forEach(key => {
            newProduct[key] = product[key];
            if (key === "상품명") {
                newProduct["색상"] = [];
            }
        });
        jsonData.products_new[index] = newProduct;
    }
});

// 업데이트된 JSON 파일 저장
fs.writeFileSync('./crocs_products_신상품_with_colors.json', JSON.stringify(jsonData, null, 4), 'utf8');

console.log('색상 정보가 추가된 JSON 파일이 생성되었습니다: crocs_products_신상품_with_colors.json');
console.log(`총 ${colorData.length}개 상품의 색상 정보를 처리했습니다.`);

// 색상 정보 확인
colorData.forEach((item, index) => {
    if (item.colors.length > 0) {
        console.log(`상품 ID ${item.productId}: ${item.colors.join(', ')}`);
    }
});