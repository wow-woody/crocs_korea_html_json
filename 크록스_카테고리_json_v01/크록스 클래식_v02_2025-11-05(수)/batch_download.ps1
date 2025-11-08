$json = Get-Content "크록스_상품목록_최종.json" -Encoding UTF8 | ConvertFrom-Json

Write-Host "Starting batch image download..." -ForegroundColor Green
Write-Host "Total products: $($json.Count)" -ForegroundColor Yellow

$downloaded = 0
$failed = 0

for ($i = 0; $i -lt $json.Count; $i++) {
    $product = $json[$i]
    $productNum = $product."번호"
    $productName = $product."상품명"
    $productImages = $product."상품 이미지"
    
    $cleanName = $productName -replace '[<>:"/\\|?*]', '' -replace '\s+', '_'
    
    Write-Host "[$($i+1)/$($json.Count)] Product $productNum : $productName" -ForegroundColor Cyan
    
    if ($productImages -and $productImages.Count -gt 0) {
        for ($j = 0; $j -lt $productImages.Count; $j++) {
            $imageUrl = $productImages[$j]
            $fileName = "${productNum}_${cleanName}_$($j+1).jpg"
            $filePath = "images\$fileName"
            
            if (!(Test-Path $filePath)) {
                Write-Host "  Downloading: $fileName" -ForegroundColor Yellow
                try {
                    Invoke-WebRequest -Uri $imageUrl -OutFile $filePath -TimeoutSec 30 -ErrorAction Stop
                    Write-Host "  Success: $fileName" -ForegroundColor Green
                    $downloaded++
                }
                catch {
                    Write-Host "  Failed: $fileName - $($_.Exception.Message)" -ForegroundColor Red
                    $failed++
                }
            }
            else {
                Write-Host "  Exists: $fileName" -ForegroundColor DarkYellow
            }
        }
    }
    else {
        Write-Host "  No images found" -ForegroundColor DarkYellow
    }
    
    if (($i + 1) % 10 -eq 0) {
        Write-Host "Progress: $($i + 1)/$($json.Count) - Downloaded: $downloaded, Failed: $failed" -ForegroundColor Magenta
    }
}

Write-Host "Batch download completed!" -ForegroundColor Green
Write-Host "Total downloaded: $downloaded" -ForegroundColor Green
Write-Host "Total failed: $failed" -ForegroundColor Red