# Placeholder Image Generator
Add-Type -AssemblyName System.Drawing

# Create a simple placeholder image
$width = 400
$height = 400
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Set background color (light gray)
$backgroundColor = [System.Drawing.Color]::LightGray
$graphics.Clear($backgroundColor)

# Draw border
$borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Gray, 2)
$graphics.DrawRectangle($borderPen, 1, 1, $width-2, $height-2)

# Draw text
$font = New-Object System.Drawing.Font("Arial", 24, [System.Drawing.FontStyle]::Bold)
$textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Gray)
$text = "NO IMAGE"
$textSize = $graphics.MeasureString($text, $font)
$textX = ($width - $textSize.Width) / 2
$textY = ($height - $textSize.Height) / 2
$graphics.DrawString($text, $font, $textBrush, $textX, $textY)

# Save the image
$outputPath = "images\placeholder.jpg"
$bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)

# Cleanup
$graphics.Dispose()
$bitmap.Dispose()
$borderPen.Dispose()
$font.Dispose()
$textBrush.Dispose()

Write-Host "Placeholder image created: $outputPath"