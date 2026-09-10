$ErrorActionPreference = 'Stop'

# Builds the current camera-ready manuscripts. The SNAS-format paper and the
# standalone abstract need XeLaTeX (Times New Roman via fontspec); the IEEE
# variant uses pdfLaTeX and needs a third pass to settle float placement.

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$paperDir = Join-Path $root 'paper\snas'
$tempDir = Join-Path $root 'tmp\pdfs'
$outputDir = Join-Path $root 'output\pdf'

New-Item -ItemType Directory -Force -Path $tempDir, $outputDir | Out-Null

Push-Location $paperDir
try {
    $sources = @(
        @{ File = 'SNAS_2026_FaithBench_short_paper.tex';      Engine = 'xelatex';  Passes = 2 },
        @{ File = 'SNAS_2026_FaithBench_abstract_blind.tex';   Engine = 'xelatex';  Passes = 2 },
        @{ File = 'SNAS_2026_FaithBench_camera_ready_ieee.tex'; Engine = 'pdflatex'; Passes = 3 }
    )

    foreach ($source in $sources) {
        $file = $source.File
        1..$source.Passes | ForEach-Object {
            & $source.Engine -interaction=nonstopmode -halt-on-error "-output-directory=$tempDir" $file
            if ($LASTEXITCODE -ne 0) {
                throw "$($source.Engine) failed for $file."
            }
        }

        $pdfName = [System.IO.Path]::ChangeExtension($file, '.pdf')
        Copy-Item -LiteralPath (Join-Path $tempDir $pdfName) -Destination (Join-Path $outputDir $pdfName) -Force
    }
}
finally {
    Pop-Location
}

Write-Host "Built PDFs in $outputDir"
