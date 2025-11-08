# PowerShell 스크립트로 HTML에서 JSON 생성
param(
    [string]$InputFile = "여성-클로그_2.html",
    [string]$OutputFile = "여성-클로그_2.json"
)

# HTML 파일 읽기
if (!(Test-Path $InputFile)) {
    Write-Host "파일을 찾을 수 없습니다: $InputFile" -ForegroundColor Red
    exit 1
}

$htmlContent = Get-Content -Path $InputFile -Raw -Encoding UTF8

# 정규식을 사용하여 각 상품 카드 추출
$cardPattern = '<div class="ok-card"[^>]*?data-pidmaster="([^"]*)"[^>]*?>.*?</div>\s*</li>'
$cards = [regex]::Matches($htmlContent, $cardPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

$products = @()
$counter = 69

foreach ($card in $cards) {
    $cardHtml = $card.Value
    
    # 상품 ID 추출
    $pidMatch = [regex]::Match($cardHtml, 'data-pidmaster="([^"]*)"')
    $productId = if ($pidMatch.Success) { $pidMatch.Groups[1].Value } else { "" }
    
    # 상품명 추출
    $nameMatch = [regex]::Match($cardHtml, '<div class="ok-card__product-name"[^>]*?>([^<]*)</div>')
    $productName = if ($nameMatch.Success) { $nameMatch.Groups[1].Value.Trim() } else { "" }
    
    # 색상 추출
    $colorMatches = [regex]::Matches($cardHtml, 'style="background:\s*rgb\(([^)]+)\)')
    $colors = @()
    foreach ($colorMatch in $colorMatches) {
        $rgbValues = $colorMatch.Groups[1].Value
        $colors += "rgb($rgbValues)"
    }
    
    # 가격 정보 추출
    $pricePattern = '<span class="ok-card__price-value[^"]*"[^>]*?>([^<]*)</span>'
    $priceMatches = [regex]::Matches($cardHtml, $pricePattern)
    
    $price = ""
    $salePrice = ""
    $discountedPrice = ""
    $priceValue = ""
    
    foreach ($priceMatch in $priceMatches) {
        $priceText = $priceMatch.Groups[1].Value.Trim()
        $priceClass = $priceMatch.Groups[0].Value
        
        if ($priceClass -match 'ok-card__price-value--sale') {
            $salePrice = $priceText
        } elseif ($priceClass -match 'ok-card__price-value--discounted') {
            $discountedPrice = $priceText
        } elseif ($priceClass -match 'ok-card__price-value--bold' -and $priceClass -notmatch 'sale') {
            $price = $priceText
        } elseif ($priceClass -match 'ok-card__price-value' -and $priceClass -notmatch 'bold|sale|discounted') {
            $priceValue = $priceText
        }
    }
    
    # 할인~ 추출
    $priceToMatch = [regex]::Match($cardHtml, '<span class="ok-card__price-to"[^>]*?>([^<]*)</span>')
    $priceTo = if ($priceToMatch.Success) { $priceToMatch.Groups[1].Value.Trim() } else { "" }
    
    # 리뷰수 추출
    $reviewMatch = [regex]::Match($cardHtml, '<div class="ok-star-ratings__ratings-reviewcount"[^>]*?>\s*\(([^)]*)\)')
    $reviewCount = if ($reviewMatch.Success) { $reviewMatch.Groups[1].Value.Trim() } else { "" }
    
    # 카테고리 추출
    $categoryMatch = [regex]::Match($cardHtml, '<div class="ok-card__snipe"[^>]*?><span[^>]*?>([^<]*)</span>')
    $category = if ($categoryMatch.Success) { $categoryMatch.Groups[1].Value.Trim() } else { "" }
    
    # 이미지 URL 추출
    $imageMatches = [regex]::Matches($cardHtml, '<img[^>]*?src="([^"]*)"')
    $imageUrls = @()
    foreach ($imageMatch in $imageMatches) {
        $imageUrls += $imageMatch.Groups[1].Value
    }
    
    # 상품 객체 생성
    $product = [ordered]@{
        "번호" = $counter
        "상품 ID" = $productId
        "상품명" = $productName
        "색상" = $colors
        "가격" = $price
        "할인가 할인율" = $salePrice
        "할인~" = $priceTo
        "할인가-2" = $priceValue
        "할인 전 원가" = $discountedPrice
        "별점 이미지" = "./images/icon_start.svg"
        "리뷰수" = $reviewCount
        "카테고리" = $category
        "상품 이미지" = $imageUrls
    }
    
    $products += $product
    $counter++
}

# JSON 형식으로 변환
$jsonOutput = $products | ConvertTo-Json -Depth 10 -Compress:$false

# 파일로 저장
$jsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "총 $($products.Count)개의 상품을 추출했습니다." -ForegroundColor Green
Write-Host "JSON 파일이 생성되었습니다: $OutputFile" -ForegroundColor Green

# 첫 번째 상품 정보 출력
if ($products.Count -gt 0) {
    Write-Host "`n첫 번째 상품 정보:" -ForegroundColor Yellow
    $products[0] | ConvertTo-Json -Depth 10 | Write-Host
}