$ErrorActionPreference = 'Stop'

# Builds the current camera-ready manuscripts.
#
# The paper follows the official SNAS_main.tex template, which gets its Times
# face from newtxtext rather than fontspec, so it builds under pdfLaTeX and
# needs a BibTeX pass between LaTeX runs to resolve the apacite reference list.
#
# The standalone abstract is an internal artifact for pasting into forms; it
# still uses fontspec and therefore still needs XeLaTeX.

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$paperDir = Join-Path $root 'paper\snas'
$tempDir = Join-Path $root 'tmp\pdfs'
$outputDir = Join-Path $root 'output\pdf'

New-Item -ItemType Directory -Force -Path $tempDir, $outputDir | Out-Null

Push-Location $paperDir
try {
    # BibTeX resolves \bibliography{references} relative to its own working
    # directory, not the output directory it is handed, so point it back here.
    $env:BIBINPUTS = "$paperDir;"

    $sources = @(
        @{ File = 'SNAS_2026_FaithBench_short_paper.tex';    Engine = 'pdflatex'; Passes = 2; Bibtex = $true  },
        @{ File = 'SNAS_2026_FaithBench_abstract_blind.tex'; Engine = 'xelatex';  Passes = 2; Bibtex = $false }
    )

    foreach ($source in $sources) {
        $file = $source.File
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($file)

        # First pass records the citations BibTeX needs to see.
        & $source.Engine -interaction=nonstopmode -halt-on-error "-output-directory=$tempDir" $file
        if ($LASTEXITCODE -ne 0) {
            throw "$($source.Engine) failed for $file."
        }

        if ($source.Bibtex) {
            # BibTeX exit codes: 0 clean, 1 warnings, 2 errors, 3 fatal. Style
            # warnings should not break the build, so only fail from 2 upward.
            & bibtex (Join-Path $tempDir $stem)
            if ($LASTEXITCODE -ge 2) {
                throw "bibtex failed for $file (exit $LASTEXITCODE)."
            }
        }

        # Remaining passes settle citations, cross-references, and floats.
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
