# 누락된 상품들을 JSON에 추가하는 스크립트
$missingIds = @("205619", "205669", "207938", "209480", "209937", "210100", "210107", "210131", "210362", "210363", "210367", "210368", "210390", "210393", "210397", "210402", "210403", "210457", "210527", "210528", "210529", "210553", "210659", "210685", "210686", "210706", "211104", "211182", "211767", "211984")

$htmlContent = Get-Content "여성-클로그_2.html" -Raw -Encoding UTF8
$jsonContent = Get-Content "여성-클로그_2.json" -Raw -Encoding UTF8 | ConvertFrom-Json

$nextNumber = 117

foreach ($id in $missingIds) {
    Write-Host "Processing product ID: $id"
    
    # 상품 정보 추출을 위한 정규식 패턴
    $pattern = "data-pidmaster=`"$id`"[\s\S]*?(?=<li>|</ul>)"
    
    if ($htmlContent -match $pattern) {
        $productHtml = $matches[0]
        
        # 상품명 추출
        if ($productHtml -match 'aria-label="([^"]*)"') {
            $productName = $matches[1]
        } else { $productName = "" }
        
        # 가격 정보 추출
        $salePrice = ""
        $originalPrice = ""
        if ($productHtml -match '₩([\d,]+)\s*\((\d+)%\)') {
            $salePrice = "₩$($matches[1]) ($($matches[2])%)"
        }
        if ($productHtml -match 'price-value--discounted[^>]*>[\s\S]*?₩([\d,]+)') {
            $originalPrice = "₩$($matches[1])"
        }
        
        # 리뷰수 추출
        $reviewCount = ""
        if ($productHtml -match '\((\d+)\)\s*<span') {
            $reviewCount = $matches[1]
        }
        
        # 이미지 URL 추출
        $images = @()
        $imagePattern = 'src="(https://media\.crocs\.com/[^"]*products/' + $id + '[^"]*)"'
        $imageMatches = [regex]::Matches($productHtml, $imagePattern)
        foreach ($match in $imageMatches) {
            $images += $match.Groups[1].Value
        }
        
        # 카테고리/프로모 정보 추출
        $category = ""
        if ($productHtml -match 'ok-card__snipe.*?>([^<]*)<') {
            $category = $matches[1]
        } elseif ($productHtml -match 'ok-card__promo--text">([^<]*)<') {
            $category = $matches[1]
        }
        
        # 새 상품 객체 생성
        $newProduct = [PSCustomObject]@{
            "번호" = $nextNumber
            "상품 ID" = $id
            "상품명" = $productName
            "색상" = @()
            "가격" = ""
            "할인가 할인율" = $salePrice
            "할인~" = ""
            "할인가-2" = ""
            "할인 전 원가" = $originalPrice
            "별점 이미지" = "./images/icon_start.svg"
            "리뷰수" = $reviewCount
            "카테고리" = $category
            "상품 이미지" = $images
        }
        
        $jsonContent += $newProduct
        $nextNumber++
        
        Write-Host "Added: $productName (ID: $id)"
    }
}

# JSON 파일로 저장
$jsonContent | ConvertTo-Json -Depth 10 | Set-Content "여성-클로그_2_완전판.json" -Encoding UTF8

Write-Host "완료! 총 $($jsonContent.Count)개 상품이 저장되었습니다."