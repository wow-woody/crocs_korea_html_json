# Image Download Script
param(
    [string]$WorkingPath = "C:\Users\jjeon\OneDrive\김정우\크록스-자료 관련 - 집\크록스\02-상품리스트-js파일\여성\여성-클로그"
)

Set-Location $WorkingPath

# Disable progress bar for faster downloads
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== Crocs Product Image Download Script ===" -ForegroundColor Green
Write-Host "Working Path: $WorkingPath" -ForegroundColor Yellow

# Load JSON files
Write-Host "`n1. Loading JSON files..." -ForegroundColor Cyan
try {
    $json1 = Get-Content "여성-클로그_1.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $json2 = Get-Content "여성-클로그_2.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host "   - File 1: $($json1.Count) products" -ForegroundColor White
    Write-Host "   - File 2: $($json2.Count) products" -ForegroundColor White
}
catch {
    Write-Host "Failed to load JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create images directory
$ImagesPath = Join-Path $WorkingPath "images"
if (-not (Test-Path $ImagesPath)) {
    New-Item -ItemType Directory -Path $ImagesPath -Force | Out-Null
    Write-Host "`n2. Images directory created" -ForegroundColor Green
} else {
    Write-Host "`n2. Images directory confirmed" -ForegroundColor Green
}

# Combine all products
$allProducts = @()
$allProducts += $json1
$allProducts += $json2

Write-Host "`n3. Starting download for $($allProducts.Count) products" -ForegroundColor Cyan

$downloadCount = 0
$errorCount = 0

foreach ($product in $allProducts) {
    $productNumber = $product.'번호'
    $productName = $product.'상품명'
    
    # Clean filename
    $safeName = $productName -replace '[\\/:"*?<>|]', '_'
    $safeName = $safeName -replace '\s+', '_'
    
    Write-Host "`nProduct $productNumber : $productName" -ForegroundColor Yellow
    
    # Process product images
    $imageUrls = @()
    if ($product.'상품 이미지' -is [array]) {
        $imageUrls = $product.'상품 이미지'
    } elseif ($product.'상품 이미지' -and $product.'상품 이미지' -ne "") {
        $imageUrls = @($product.'상품 이미지')
    }
    
    if ($imageUrls.Count -eq 0) {
        Write-Host "   - No image URLs found" -ForegroundColor Gray
        continue
    }
    
    $imageIndex = 1
    foreach ($imageUrl in $imageUrls) {
        if (-not $imageUrl -or $imageUrl.Trim() -eq "") {
            continue
        }
        
        try {
            # Extract file extension
            $extension = ".jpg"
            if ($imageUrl -match '\.(jpg|jpeg|png|gif|webp)(\?|$)') {
                $extension = ".$($matches[1])"
            }
            
            # Filename: Number_ProductName_Index.extension
            $fileName = "${productNumber}_${safeName}_${imageIndex}${extension}"
            $filePath = Join-Path $ImagesPath $fileName
            
            Write-Host "   - Downloading: $fileName" -NoNewline
            
            # Download image
            Invoke-WebRequest -Uri $imageUrl -OutFile $filePath -UseBasicParsing
            $downloadCount++
            Write-Host " Success" -ForegroundColor Green
            
            $imageIndex++
        }
        catch {
            Write-Host " Failed: $($_.Exception.Message)" -ForegroundColor Red
            $errorCount++
        }
    }
}

Write-Host "`n=== Download Complete ===" -ForegroundColor Green
Write-Host "Success: $downloadCount files" -ForegroundColor Green
Write-Host "Failed: $errorCount files" -ForegroundColor Red
Write-Host "Images saved to: $ImagesPath" -ForegroundColor Yellow

# Restore progress preference
$ProgressPreference = 'Continue'