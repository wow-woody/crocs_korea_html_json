# PowerShell 스크립트로 HTML에서 상품 정보 추출
$htmlFile = "신상품&트렌드.html"
$outputFile = "크록스_상품목록_전체.json"

# HTML 파일 읽기
$htmlContent = Get-Content -Path $htmlFile -Raw -Encoding UTF8

# 정규식 패턴으로 상품 카드 찾기
$cardPattern = '<div class="ok-card"[^>]*aria-label="([^"]*)"[^>]*data-pidmaster="([^"]*)"[^>]*>(.*?)</div>\s*</li>'
$cardMatches = [regex]::Matches($htmlContent, $cardPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

$products = @()
$productNumber = 1

foreach ($match in $cardMatches) {
    $productName = $match.Groups[1].Value
    $productId = $match.Groups[2].Value
    $cardContent = $match.Groups[3].Value
    
    # 색상 정보 추출
    $colorPattern = '<li class="ok-card__swatch-color"[^>]*style="[^"]*background:\s*([^;"]*)'
    $colorMatches = [regex]::Matches($cardContent, $colorPattern)
    $colors = @()
    foreach ($colorMatch in $colorMatches) {
        $colorValue = $colorMatch.Groups[1].Value.Trim()
        if ($colorValue -match 'rgb\(\d+,\s*\d+,\s*\d+\)') {
            $colors += $colorValue
        }
    }
    
    # 가격 정보 추출
    $pricePattern = '<span[^>]*class="[^"]*ok-card__price-value[^"]*ok-card__price-value--bold[^"]*"[^>]*>([^<]*)</span>'
    $priceMatches = [regex]::Matches($cardContent, $pricePattern)
    $regularPrice = ""
    $salePrice = ""
    
    # 할인 가격 확인
    $salePattern = '<span[^>]*class="[^"]*ok-card__price-value--sale[^"]*"[^>]*>([^<]*)</span>'
    $saleMatch = [regex]::Match($cardContent, $salePattern)
    if ($saleMatch.Success) {
        $salePrice = $saleMatch.Groups[1].Value.Trim()
    }
    
    # 일반 가격
    foreach ($priceMatch in $priceMatches) {
        $priceText = $priceMatch.Groups[1].Value.Trim()
        if ($priceText -notmatch '\(.*\)' -and $priceText -ne "") {
            $regularPrice = $priceText
            break
        }
    }
    
    # 할인 전 원가
    $originalPricePattern = '<span[^>]*class="[^"]*ok-card__price-value--discounted[^"]*"[^>]*>.*?</span>([^<]*)</span>'
    $originalPriceMatch = [regex]::Match($cardContent, $originalPricePattern)
    $originalPrice = ""
    if ($originalPriceMatch.Success) {
        $originalPrice = $originalPriceMatch.Groups[1].Value.Trim()
    }
    
    # 리뷰수 추출
    $reviewPattern = '<div class="ok-star-ratings__ratings-reviewcount"[^>]*>.*?\((\d+)\)'
    $reviewMatch = [regex]::Match($cardContent, $reviewPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $reviewCount = ""
    if ($reviewMatch.Success) {
        $reviewCount = $reviewMatch.Groups[1].Value
    }
    
    # 카테고리 추출
    $categoryPattern = '<div class="ok-card__snipe"[^>]*>.*?<span[^>]*>([^<]*)</span>'
    $categoryMatch = [regex]::Match($cardContent, $categoryPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $category = ""
    if ($categoryMatch.Success) {
        $category = $categoryMatch.Groups[1].Value.Trim()
    }
    
    # 상품 이미지 추출
    $imagePattern = '<div class="ok-card__image-wrap"[^>]*>(.*?)</div>'
    $imageWrapMatch = [regex]::Match($cardContent, $imagePattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $images = @()
    if ($imageWrapMatch.Success) {
        $imageContent = $imageWrapMatch.Groups[1].Value
        $srcPattern = '<img[^>]*src="([^"]*)"'
        $srcMatches = [regex]::Matches($imageContent, $srcPattern)
        foreach ($srcMatch in $srcMatches) {
            $images += $srcMatch.Groups[1].Value
        }
    }
    
    # 상품 객체 생성
    $product = [PSCustomObject]@{
        "number" = $productNumber
        "productId" = $productId
        "productName" = $productName
        "colors" = $colors
        "price" = if ($regularPrice -ne "") { $regularPrice } elseif ($salePrice -ne "") { ($salePrice -split '\(')[0].Trim() } else { "" }
        "salePrice" = $salePrice
        "originalPrice" = $originalPrice
        "starImage" = "크록스 클래식_v02_2025-11-05(수)\images\icon_start.svg"
        "reviewCount" = $reviewCount
        "category" = $category
        "productImages" = $images
    }
    
    $products += $product
    $productNumber++
    
    Write-Host "상품 $($productNumber-1) 처리 완료: $productName"
}

# JSON으로 변환하여 저장
$jsonOutput = $products | ConvertTo-Json -Depth 10 -Compress:$false
$jsonOutput | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host ""
Write-Host "총 $($products.Count)개의 상품을 추출하여 '$outputFile' 파일로 저장했습니다."

# 첫 번째 상품 정보 출력
if ($products.Count -gt 0) {
    Write-Host ""
    Write-Host "첫 번째 상품 예시:"
    $products[0] | ConvertTo-Json -Depth 10
}