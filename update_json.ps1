# Update JSON with local image paths
$jsonPath = "크록스 클래식\crocs_products_신상품.json"
$json = Get-Content -Path $jsonPath -Encoding UTF8 | ConvertFrom-Json

# Update each product's image path
for ($i = 0; $i -lt $json.products_new.Count; $i++) {
    $product = $json.products_new[$i]
    $number = $product.'번호'
    $name = $product.'상품명' -replace '[\\/:*?"<>|&]', '_'
    $localImagePath = "./images/${number}_${name}.jpg"
    
    $json.products_new[$i].'상품 이미지' = $localImagePath
    
    Write-Host "Updated product ${number}: $localImagePath"
}

# Save updated JSON
$json | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8

Write-Host "JSON file updated with local image paths!"