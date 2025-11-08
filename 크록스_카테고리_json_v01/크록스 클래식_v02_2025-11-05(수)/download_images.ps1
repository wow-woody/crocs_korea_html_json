# Crocs Product Image Download Script
param()

$jsonContent = Get-Content "크록스_상품목록_최종.json" -Encoding UTF8 | ConvertFrom-Json

if (!(Test-Path "images")) {
    New-Item -ItemType Directory -Name "images" -Force
}

$totalItems = $jsonContent.Count
$currentItem = 0

Write-Host "Total $totalItems products to download images..." -ForegroundColor Green

foreach ($product in $jsonContent) {
    $currentItem++
    $productNumber = $product."번호"
    $productName = $product."상품명"
    $productImages = $product."상품 이미지"
    
    $cleanProductName = $productName -replace '[<>:"/\\|?*]', '' -replace '\s+', '_'
    
    Write-Host "[$currentItem/$totalItems] Product $productNumber : $productName" -ForegroundColor Cyan
    
    if ($productImages -and $productImages.Count -gt 0) {
        $imageIndex = 1
        
        foreach ($imageUrl in $productImages) {
            try {
                $fileName = "${productNumber}_${cleanProductName}_${imageIndex}"
                
                $extension = ".jpg"
                if ($imageUrl -match '\.(jpg|jpeg|png|gif|webp)') {
                    $extension = ".$($matches[1])"
                }
                
                $fullFileName = "${fileName}${extension}"
                $filePath = "images\$fullFileName"
                
                if (!(Test-Path $filePath)) {
                    Write-Host "  Downloading image $imageIndex : $fullFileName" -ForegroundColor Yellow
                    
                    Invoke-WebRequest -Uri $imageUrl -OutFile $filePath -ErrorAction Stop
                    
                    Write-Host "  Success: $fullFileName" -ForegroundColor Green
                } else {
                    Write-Host "  File exists: $fullFileName" -ForegroundColor DarkYellow
                }
                
                $imageIndex++
            }
            catch {
                Write-Host "  Failed: $imageUrl" -ForegroundColor Red
                Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  No image URLs found." -ForegroundColor DarkYellow
    }
    
    $progress = [math]::Round(($currentItem / $totalItems) * 100, 1)
    Write-Host "Progress: $progress% ($currentItem/$totalItems)" -ForegroundColor Magenta
    Write-Host "----------------------------------------"
}

Write-Host "All images download completed!" -ForegroundColor Green
Write-Host "Files saved in images folder." -ForegroundColor Green