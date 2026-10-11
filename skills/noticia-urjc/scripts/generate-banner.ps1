<#
.SYNOPSIS
    Genera una imagen de cabecera/banner 1200x800 con franjas graficas institucionales y
    titulo, cuando no hay foto disponible.

.DESCRIPTION
    Dibuja directamente sobre un Bitmap con System.Drawing (no depende de Python/ImageMagick/Inkscape).
    Pensado como alternativa al MODO FOTO del skill noticia-urjc cuando el usuario pide un "diseno"
    en lugar de aportar una fotografia.

    Sigue el Manual de identidad visual de la URJC: fondo en positivo (claro), franjas graficas
    de color como elemento de jerarquia -no una ilustracion tematica-, tipografia Inter (cargada
    desde los .ttf empaquetados en assets/, sin necesidad de instalarla en el sistema) y el
    logotipo de la Escuela. Ver okf/identidad-corporativa.md de este plugin.

    El color de marca de la URJC (rojo PANTONE 485C, #CB0017) es fijo. El segundo color de banda
    es el propio de cada Escuela y se pasa con -BrandColor (hex); por defecto usa el marron/ocre
    de ejemplo de la ETSII (#8C6239) si no se indica otro.

.PARAMETER Title
    Texto principal del banner (normalmente el titulo de la noticia, o una version corta del mismo).

.PARAMETER OutputPath
    Ruta del PNG de salida.

.PARAMETER Kicker
    Texto pequeno sobre el titulo (normalmente "<SIGLAS ESCUELA> - Universidad Rey Juan Carlos").

.PARAMETER BrandColor
    Color hex (RRGGBB o #RRGGBB) de la gama cromatica propia de la Escuela. Por defecto #8C6239
    (marron de ejemplo de la ETSII).

.PARAMETER Width
    Ancho en pixeles, por defecto 1200.

.PARAMETER Height
    Alto en pixeles, por defecto 800.

.PARAMETER LogoPath
    Ruta opcional a un logo PNG a superponer en la esquina superior izquierda. Si no se indica,
    se busca automaticamente ..\assets\logo-ejemplo.png junto a este script (sustituir por
    el logo de la Escuela real); si no existe, se omite sin error.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File generate-banner.ps1 -Title "La Escuela acoge la final del hackathon" -Kicker "ETSII - Universidad Rey Juan Carlos" -BrandColor "#8C6239" -LogoPath "C:\ruta\logo-escuela.png" -OutputPath "C:\salida\banner.png"
#>
param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [string]$Kicker = "Universidad Rey Juan Carlos",
    [string]$BrandColor = "#8C6239",
    [int]$Width = 1200,
    [int]$Height = 800,
    [string]$LogoPath
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

function ConvertFrom-HexColor {
    param([string]$Hex)
    $Hex = $Hex.TrimStart('#')
    if ($Hex.Length -ne 6) { throw "Color hex invalido: $Hex (esperado RRGGBB)" }
    $r = [Convert]::ToInt32($Hex.Substring(0, 2), 16)
    $g = [Convert]::ToInt32($Hex.Substring(2, 2), 16)
    $b = [Convert]::ToInt32($Hex.Substring(4, 2), 16)
    return [System.Drawing.Color]::FromArgb(255, $r, $g, $b)
}

$brandColorValue = ConvertFrom-HexColor $BrandColor

$assetsDir = Join-Path (Split-Path -Parent $PSScriptRoot) "assets"

$outDir = Split-Path -Parent $OutputPath
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

if (-not $LogoPath) {
    $defaultLogo = Join-Path $assetsDir "logo-ejemplo.png"
    if (Test-Path -LiteralPath $defaultLogo) { $LogoPath = $defaultLogo }
}

# Tipografia Inter (estatica, pesos Regular/Medium/Bold del Manual), cargada desde los
# .ttf empaquetados junto al skill via PrivateFontCollection -no requiere instalarla en
# el sistema-. Si faltan los ficheros, se cae a Segoe UI (la mas cercana preinstalada
# en Windows), coherente con la politica de sustituta del Manual cuando no hay Inter.
#
# OJO: cada .ttf declara su propia familia -Inter-Bold.ttf enlaza como estilo "Bold" de
# la familia "Inter" (con Inter-Regular.ttf ausente, solo queda ese estilo disponible),
# pero Inter-Medium.ttf declara su PROPIA familia "Inter Medium" en estilo "Regular": el
# enlace de estilos clasico (name table 1/2) solo cubre Regular/Bold/Italic/BoldItalic,
# no pesos intermedios. Por eso se usan dos objetos FontFamily distintos, no uno con dos
# estilos.
$privateFonts = New-Object System.Drawing.Text.PrivateFontCollection
$interBoldPath = Join-Path $assetsDir "Inter-Bold.ttf"
$interMediumPath = Join-Path $assetsDir "Inter-Medium.ttf"
$haveInter = (Test-Path -LiteralPath $interBoldPath) -and (Test-Path -LiteralPath $interMediumPath)
if ($haveInter) {
    $privateFonts.AddFontFile($interBoldPath)
    $privateFonts.AddFontFile($interMediumPath)
    $boldFamily = $privateFonts.Families | Where-Object { $_.Name -eq "Inter" } | Select-Object -First 1
    $mediumFamily = $privateFonts.Families | Where-Object { $_.Name -eq "Inter Medium" } | Select-Object -First 1
    $boldStyle = [System.Drawing.FontStyle]::Bold
    $mediumStyle = [System.Drawing.FontStyle]::Regular
}
else {
    $boldFamily = New-Object System.Drawing.FontFamily("Segoe UI")
    $mediumFamily = $boldFamily
    $boldStyle = [System.Drawing.FontStyle]::Bold
    $mediumStyle = [System.Drawing.FontStyle]::Regular
}

function Get-WrappedLines {
    param($Graphics, [string]$Text, $Font, [double]$MaxWidth)
    $words = $Text -split '\s+'
    $lines = New-Object System.Collections.Generic.List[string]
    $current = ""
    foreach ($word in $words) {
        $test = if ($current -eq "") { $word } else { "$current $word" }
        $size = $Graphics.MeasureString($test, $Font)
        if ($size.Width -gt $MaxWidth -and $current -ne "") {
            $lines.Add($current)
            $current = $word
        }
        else {
            $current = $test
        }
    }
    if ($current -ne "") { $lines.Add($current) }
    return $lines
}

$bitmap = New-Object System.Drawing.Bitmap($Width, $Height)
$g = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic

    # Fondo en positivo (Manual de identidad visual): blanco, no degradado
    $paperBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
    $g.FillRectangle($paperBrush, 0, 0, $Width, $Height)
    $paperBrush.Dispose()

    # Franjas graficas: el elemento distintivo de jerarquia del Manual, no una
    # ilustracion tematica. Roja (PANTONE 485 C, marca URJC) + color propio de la Escuela.
    $redBandH = [math]::Max(6, [int]($Height * 0.0175))
    $brandBandH = [math]::Max(3, [int]($Height * 0.0075))
    $redBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 203, 0, 23))
    $brandBrush = New-Object System.Drawing.SolidBrush($brandColorValue)
    $g.FillRectangle($redBrush, 0, 0, $Width, $redBandH)
    $g.FillRectangle($brandBrush, 0, $redBandH, $Width, $brandBandH)
    $redBrush.Dispose()
    $brandBrush.Dispose()
    $bandsBottom = $redBandH + $brandBandH

    $marginX = [int]($Width * 0.0533)
    $maxTextWidth = $Width - (2 * $marginX)

    # Logo opcional, esquina superior izquierda, debajo de las franjas
    $logoBottom = $bandsBottom + [int]($Height * 0.045) + [int]($Height * 0.065)
    if ($LogoPath -and (Test-Path -LiteralPath $LogoPath)) {
        $logo = [System.Drawing.Image]::FromFile((Resolve-Path -LiteralPath $LogoPath).Path)
        try {
            $maxLogoHeight = [int]($Height * 0.065)
            $scale = $maxLogoHeight / [double]$logo.Height
            $logoW = [int]($logo.Width * $scale)
            $logoH = $maxLogoHeight
            $pasteY = $bandsBottom + [int]($Height * 0.045)
            $g.DrawImage($logo, $marginX, $pasteY, $logoW, $logoH)
            $logoBottom = $pasteY + $logoH + [int]($Height * 0.025)
        }
        finally {
            $logo.Dispose()
        }
    }

    # Kicker (texto pequeno sobre el titulo), en rojo de marca
    $kickerFont = New-Object System.Drawing.Font($mediumFamily, [int]($Height * 0.02), $mediumStyle)
    $kickerBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 203, 0, 23))
    $kickerY = [math]::Max($logoBottom, $bandsBottom + [int]($Height * 0.14))
    $g.DrawString($Kicker.ToUpperInvariant(), $kickerFont, $kickerBrush, $marginX, $kickerY)
    $kickerHeight = $g.MeasureString($Kicker, $kickerFont).Height

    # Titulo: autoajuste de tamano de fuente hasta que quepa en el area segura, en negro
    $titleTop = $kickerY + $kickerHeight + [int]($Height * 0.025)
    $titleMaxHeight = $Height - $titleTop - [int]($Height * 0.08)

    $titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 20, 17, 15))
    $lines = $null
    $chosenFont = $null
    $fontSizes = @(0.08, 0.0725, 0.065, 0.0575, 0.05, 0.0425, 0.0375, 0.0325) | ForEach-Object { [int]($Height * $_) }
    foreach ($fontSize in $fontSizes) {
        $font = New-Object System.Drawing.Font($boldFamily, $fontSize, $boldStyle)
        $candidateLines = Get-WrappedLines -Graphics $g -Text $Title -Font $font -MaxWidth $maxTextWidth
        $lineHeight = $font.GetHeight($g)
        $totalHeight = $lineHeight * $candidateLines.Count
        if ($totalHeight -le $titleMaxHeight -or $fontSize -eq $fontSizes[-1]) {
            $chosenFont = $font
            $lines = $candidateLines
            break
        }
        $font.Dispose()
    }

    $lineHeight = $chosenFont.GetHeight($g)
    $totalHeight = $lineHeight * $lines.Count
    $startY = $titleTop + [math]::Max(0, ($titleMaxHeight - $totalHeight) / 2.0)

    $y = $startY
    foreach ($line in $lines) {
        $g.DrawString($line, $chosenFont, $titleBrush, $marginX, $y)
        $y += $lineHeight
    }

    $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)

    $usedFontSize = $chosenFont.Size
    $kickerFont.Dispose()
    $kickerBrush.Dispose()
    $titleBrush.Dispose()
    $chosenFont.Dispose()
    $privateFonts.Dispose()

    Write-Output "OK: banner guardado en $OutputPath ($Width x $Height, fuente titulo ${usedFontSize}pt, $($lines.Count) linea(s))"
}
finally {
    $g.Dispose()
    $bitmap.Dispose()
}
