param(
    [Parameter(Mandatory = $true)]
    [string] $PackagePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resolvedPackage = Resolve-Path -LiteralPath $PackagePath
$path = $resolvedPackage.Path
$tempDir = $null

function Get-RelativePath {
    param(
        [string] $BasePath,
        [string] $FullPath
    )

    $baseUri = [System.Uri]((Join-Path (Resolve-Path -LiteralPath $BasePath).Path '.'))
    $fullUri = [System.Uri]((Resolve-Path -LiteralPath $FullPath).Path)
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($fullUri).ToString()).Replace('/', '\')
}

function Test-BlacklistedRelativePath {
    param([string] $RelativePath)

    $normalized = $RelativePath -replace '/', '\'
    $segments = @($normalized -split '\\' | Where-Object { $_ -ne '' })
    $leaf = if ($segments.Count -gt 0) { $segments[-1] } else { $normalized }

    if ($leaf -in @('llm_secrets.json', 'llm_chat_history.json', '.env')) {
        return $true
    }

    if ($leaf -like '*.env') {
        return $true
    }

    if ($leaf -like '*.pyc') {
        return $true
    }

    if ($leaf -like '*.log') {
        return $true
    }

    foreach ($segment in $segments) {
        if ($segment -in @('data', 'logs', 'build', 'dist', '__pycache__', 'peakdesk-sprite')) {
            return $true
        }
    }

    return $false
}

function Assert-RequiredRelativePath {
    param(
        [string[]] $RelativePaths,
        [string] $RequiredPath
    )

    $normalizedRequired = $RequiredPath -replace '/', '\'
    $hasRequiredPath = $false
    foreach ($relativePath in $RelativePaths) {
        if ($relativePath -eq $normalizedRequired -or $relativePath.EndsWith("\" + $normalizedRequired, [System.StringComparison]::OrdinalIgnoreCase)) {
            $hasRequiredPath = $true
            break
        }
    }

    if (-not $hasRequiredPath) {
        throw "Release package audit failed. Required path missing: $normalizedRequired"
    }
}

try {
    if (Test-Path -LiteralPath $path -PathType Container) {
        $scanRoot = $path
        $items = Get-ChildItem -LiteralPath $scanRoot -Recurse -Force
        $relativePaths = foreach ($item in $items) {
            Get-RelativePath -BasePath $scanRoot -FullPath $item.FullName
        }
    }
    elseif ($path.ToLowerInvariant().EndsWith('.zip')) {
        $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("peakdesk-release-audit-" + [System.Guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
        Expand-Archive -LiteralPath $path -DestinationPath $tempDir -Force
        $items = Get-ChildItem -LiteralPath $tempDir -Recurse -Force
        $relativePaths = foreach ($item in $items) {
            Get-RelativePath -BasePath $tempDir -FullPath $item.FullName
        }
    }
    else {
        throw "PackagePath must be a directory or .zip file: $path"
    }

    $violations = @($relativePaths | Where-Object { Test-BlacklistedRelativePath -RelativePath $_ } | Sort-Object -Unique)

    if ($violations.Count -gt 0) {
        Write-Error ("Release package audit failed. Blacklisted paths found:`n" + ($violations -join "`n"))
    }

    $normalizedRelativePaths = @($relativePaths | ForEach-Object { $_ -replace '/', '\' })
    Assert-RequiredRelativePath -RelativePaths $normalizedRelativePaths -RequiredPath 'CodexPetLive.exe'
    Assert-RequiredRelativePath -RelativePaths $normalizedRelativePaths -RequiredPath 'res\icons'
    Assert-RequiredRelativePath -RelativePaths $normalizedRelativePaths -RequiredPath 'res\role'
    Assert-RequiredRelativePath -RelativePaths $normalizedRelativePaths -RequiredPath 'res\language'

    Write-Host "[audit] PASS: no blacklisted paths found in $path"
}
finally {
    if ($tempDir -and (Test-Path -LiteralPath $tempDir)) {
        $resolvedTemp = (Resolve-Path -LiteralPath $tempDir).Path
        $systemTemp = [System.IO.Path]::GetTempPath()
        if (-not $resolvedTemp.StartsWith($systemTemp, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected temporary directory: $resolvedTemp"
        }
        Remove-Item -LiteralPath $tempDir -Recurse -Force
    }
}
