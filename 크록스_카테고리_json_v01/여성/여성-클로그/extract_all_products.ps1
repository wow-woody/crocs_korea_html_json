# PowerShell 스크립트 - 모든 상품을 추출하여 JSON 생성
param(
    [string]$InputFile = "여성-클로그_2.html",
    [string]$OutputFile = "여성-클로그_2.json"
)

Write-Host "HTML 파일에서 모든 상품 정보를 추출 중..." -ForegroundColor Green

# HTML 파일 읽기
$htmlContent = Get-Content -Path $InputFile -Raw -Encoding UTF8

# 모든 상품 카드 추출 (더 정확한 패턴)
$cardPattern = '<li>\s*<div class="ok-card"[^>]*?data-pidmaster="([^"]*)"[^>]*?>(.*?)(?=<li>|</ul>)'
$cardMatches = [regex]::Matches($htmlContent, $cardPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

Write-Host "발견된 상품 수: $($cardMatches.Count)" -ForegroundColor Yellow

$products = @()
$counter = 69

foreach ($match in $cardMatches) {
    $productId = $match.Groups[1].Value
    $cardContent = $match.Groups[2].Value
    
    # 중복 제거 체크
    $isDuplicate = $false
    foreach ($existing in $products) {
        if ($existing."상품 ID" -eq $productId) {
            $isDuplicate = $true
            break
        }
    }
    
    if ($isDuplicate) {
        continue
    }
    
    Write-Host "처리 중: 상품 ID $productId" -ForegroundColor Gray
    
    # 상품명 추출 (aria-label에서)
    $nameMatch = [regex]::Match($cardContent, 'aria-label="([^"]*)"')
    $productName = if ($nameMatch.Success) { $nameMatch.Groups[1].Value } else { "" }
    
    # 색상 추출 (style="background: rgb(...)" 패턴)
    $colorMatches = [regex]::Matches($cardContent, 'style="background:\s*rgb\(([^)]+)\)')
    $colors = @()
    foreach ($colorMatch in $colorMatches) {
        $rgbValues = $colorMatch.Groups[1].Value.Trim()
        $colors += "rgb($rgbValues)"
    }
    
    # 가격 정보 추출
    $pricePattern = '<span class="ok-card__price-value[^"]*"[^>]*?>([^<]*?)</span>'
    $priceMatches = [regex]::Matches($cardContent, $pricePattern)
    
    $price = ""
    $salePrice = ""
    $discountedPrice = ""
    $priceValue = ""
    $priceTo = ""
    
    # 할인~ 추출
    $priceToMatch = [regex]::Match($cardContent, '<span class="ok-card__price-to"[^>]*?>([^<]*?)</span>')
    if ($priceToMatch.Success) {
        $priceTo = $priceToMatch.Groups[1].Value.Trim()
    }
    
    foreach ($priceMatch in $priceMatches) {
        $priceText = $priceMatch.Groups[1].Value.Trim()
        $priceClass = $priceMatch.Groups[0].Value
        
        if ($priceClass -match 'ok-card__price-value--sale') {
            if ($priceText -notmatch '^\s*$' -and $salePrice -eq "") {
                $salePrice = $priceText
            }
        } elseif ($priceClass -match 'ok-card__price-value--discounted') {
            $discountedPrice = $priceText
        } elseif ($priceClass -match 'ok-card__price-value--bold' -and $priceClass -notmatch 'sale') {
            $price = $priceText
        } elseif ($priceClass -match 'ok-card__price-value' -and $priceClass -notmatch 'bold|sale|discounted') {
            if ($priceValue -eq "") {
                $priceValue = $priceText
            }
        }
    }
    
    # 리뷰수 추출
    $reviewMatch = [regex]::Match($cardContent, '<div class="ok-star-ratings__ratings-reviewcount"[^>]*?>\s*\(([^)]*)\)')
    $reviewCount = if ($reviewMatch.Success) { $reviewMatch.Groups[1].Value.Trim() } else { "" }
    
    # 카테고리 추출 (ok-card__snipe > span)
    $categoryMatch = [regex]::Match($cardContent, '<div class="ok-card__snipe"[^>]*?><span[^>]*?>([^<]*?)</span>')
    $category = if ($categoryMatch.Success) { $categoryMatch.Groups[1].Value.Trim() } else { "" }
    
    # 이미지 URL 추출
    $imageMatches = [regex]::Matches($cardContent, '<img[^>]*?src="([^"]*?)"')
    $imageUrls = @()
    foreach ($imageMatch in $imageMatches) {
        $url = $imageMatch.Groups[1].Value
        if ($url -and $url -notmatch '^\s*$') {
            $imageUrls += $url
        }
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

Write-Host "총 $($products.Count)개의 고유 상품을 처리했습니다." -ForegroundColor Green

# JSON 형식으로 변환 및 저장
$jsonOutput = $products | ConvertTo-Json -Depth 10 -Compress:$false

# UTF-8 BOM 없이 저장
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Resolve-Path $OutputFile), $jsonOutput, $utf8NoBom)

Write-Host "JSON 파일이 생성되었습니다: $OutputFile" -ForegroundColor Green

# 첫 5개 상품 정보 출력
Write-Host "`n처음 5개 상품:" -ForegroundColor Yellow
for ($i = 0; $i -lt [Math]::Min(5, $products.Count); $i++) {
    Write-Host "[$($products[$i].'번호')] $($products[$i].'상품명') - ID: $($products[$i].'상품 ID')" -ForegroundColor Cyan
}