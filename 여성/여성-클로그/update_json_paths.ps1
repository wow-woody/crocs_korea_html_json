# JSON 파일의 이미지 경로 업데이트 스크립트
param(
    [string]$WorkingPath = "C:\Users\jjeon\OneDrive\김정우\크록스-자료 관련 - 집\크록스\02-상품리스트-js파일\여성\여성-클로그"
)

Set-Location $WorkingPath

Write-Host "=== JSON 이미지 경로 업데이트 스크립트 ===" -ForegroundColor Green

# 1. 여성-클로그_1.json 업데이트
Write-Host "`n1. 여성-클로그_1.json 업데이트 중..." -ForegroundColor Cyan
$json1 = Get-Content "여성-클로그_1.json" -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($product in $json1) {
    $number = $product.'번호'
    $name = $product.'상품명' -replace '[\\/:"*?<>|&]', '_' -replace '\s+', '_'
    
    # 해당 이미지 파일이 존재하는지 확인
    $imageFile = "images\${number}_${name}_1.jpg"
    if (Test-Path $imageFile) {
        $product.'상품 이미지' = "./images/${number}_${name}_1.jpg"
        Write-Host "  Updated Product $number" -ForegroundColor Green
    } else {
        Write-Host "  Missing image for Product $number" -ForegroundColor Yellow
    }
}

# JSON1 저장
$json1 | ConvertTo-Json -Depth 10 | Out-File "여성-클로그_1.json" -Encoding UTF8
Write-Host "여성-클로그_1.json 업데이트 완료!" -ForegroundColor Green

# 2. 여성-클로그_2.json 업데이트
Write-Host "`n2. 여성-클로그_2.json 업데이트 중..." -ForegroundColor Cyan
$json2 = Get-Content "여성-클로그_2.json" -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($product in $json2) {
    $number = $product.'번호'
    $name = $product.'상품명' -replace '[\\/:"*?<>|&]', '_' -replace '\s+', '_'
    
    # 이미지 배열 생성
    $localImages = @()
    $imageIndex = 1
    
    while ($true) {
        $imageFile = "images\${number}_${name}_${imageIndex}.jpg"
        if (Test-Path $imageFile) {
            $localImages += "./images/${number}_${name}_${imageIndex}.jpg"
            $imageIndex++
        } else {
            break
        }
    }
    
    if ($localImages.Count -gt 0) {
        $product.'상품 이미지' = $localImages
        Write-Host "  Updated Product $number ($($localImages.Count) images)" -ForegroundColor Green
    } else {
        Write-Host "  No images found for Product $number" -ForegroundColor Yellow
    }
}

# JSON2 저장
$json2 | ConvertTo-Json -Depth 10 | Out-File "여성-클로그_2.json" -Encoding UTF8
Write-Host "여성-클로그_2.json 업데이트 완료!" -ForegroundColor Green

Write-Host "`n=== 모든 JSON 파일 업데이트 완료! ===" -ForegroundColor Green