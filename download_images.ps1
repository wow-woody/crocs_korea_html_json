# Crocs Product Image Download Script
$jsonPath = "크록스 클래식\crocs_products_신상품.json"
$imagesPath = "크록스 클래식\images"

# Read JSON file
$jsonContent = Get-Content -Path $jsonPath -Encoding UTF8 | ConvertFrom-Json

# Download each product image
foreach ($product in $jsonContent.products_new) {
    $number = $product."번호"
    $productName = $product."상품명"
    $imageUrl = $product."상품 이미지"
    
    # Clean filename for Windows (remove special characters)
    $cleanName = $productName -replace '[\\/:*?"<>|&]', '_'
    $fileName = "${number}_${cleanName}.jpg"
    $localPath = Join-Path $imagesPath $fileName
    
    Write-Host "Downloading: $fileName"
    
    try {
        # Download image
        Invoke-WebRequest -Uri $imageUrl -OutFile $localPath -UseBasicParsing
        Write-Host "Success: $fileName" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed: $fileName - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "All images downloaded!"
