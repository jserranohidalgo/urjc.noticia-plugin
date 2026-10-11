<#
.SYNOPSIS
    Recorta (centrado) y redimensiona una imagen a un tamaño exacto, por defecto 1200x800.

.DESCRIPTION
    Pensado para preparar fotos para el campo "Imagen del item" del CMS de noticias de la ETSII,
    que espera imagenes de 1200x800 px. Hace un crop centrado para no deformar la foto y luego
    escala al tamano final con interpolacion de alta calidad.

.PARAMETER InputPath
    Ruta de la imagen original (jpg, png, etc).

.PARAMETER OutputPath
    Ruta del archivo de salida. La extension (.png o .jpg/.jpeg) determina el formato de guardado.

.PARAMETER Width
    Ancho final en pixeles. Por defecto 1200.

.PARAMETER Height
    Alto final en pixeles. Por defecto 800.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File resize-image.ps1 -InputPath "C:\fotos\evento.jpg" -OutputPath "C:\salida\evento-1200x800.png"
#>
param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [int]$Width = 1200,
    [int]$Height = 800
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "No existe el archivo de entrada: $InputPath"
}

Add-Type -AssemblyName System.Drawing

$outDir = Split-Path -Parent $OutputPath
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

$source = [System.Drawing.Image]::FromFile((Resolve-Path -LiteralPath $InputPath).Path)
try {
    $targetRatio = $Width / [double]$Height
    $sourceRatio = $source.Width / [double]$source.Height

    if ($sourceRatio -gt $targetRatio) {
        # La fuente es mas ancha de lo necesario -> recortar los lados
        $cropHeight = $source.Height
        $cropWidth = [int]([math]::Round($cropHeight * $targetRatio))
        $cropX = [int]([math]::Round(($source.Width - $cropWidth) / 2.0))
        $cropY = 0
    }
    else {
        # La fuente es mas alta de lo necesario -> recortar arriba/abajo
        $cropWidth = $source.Width
        $cropHeight = [int]([math]::Round($cropWidth / $targetRatio))
        $cropX = 0
        $cropY = [int]([math]::Round(($source.Height - $cropHeight) / 2.0))
    }

    $cropRect = New-Object System.Drawing.Rectangle($cropX, $cropY, $cropWidth, $cropHeight)

    $destBitmap = New-Object System.Drawing.Bitmap($Width, $Height)
    $destBitmap.SetResolution($source.HorizontalResolution, $source.VerticalResolution)

    $graphics = [System.Drawing.Graphics]::FromImage($destBitmap)
    try {
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $destRect = New-Object System.Drawing.Rectangle(0, 0, $Width, $Height)
        $graphics.DrawImage($source, $destRect, $cropRect, [System.Drawing.GraphicsUnit]::Pixel)
    }
    finally {
        $graphics.Dispose()
    }

    $ext = [System.IO.Path]::GetExtension($OutputPath).ToLowerInvariant()
    $format = switch ($ext) {
        ".jpg" { [System.Drawing.Imaging.ImageFormat]::Jpeg }
        ".jpeg" { [System.Drawing.Imaging.ImageFormat]::Jpeg }
        default { [System.Drawing.Imaging.ImageFormat]::Png }
    }

    $destBitmap.Save($OutputPath, $format)
    $destBitmap.Dispose()

    Write-Output "OK: imagen guardada en $OutputPath ($Width x $Height)"
}
finally {
    $source.Dispose()
}
