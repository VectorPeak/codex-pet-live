param(
    [string] $PythonPath = 'python',
    [string] $Version = '',
    [string] $Configuration = 'windowed',
    [switch] $SkipBuild,
    [switch] $SkipArchive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path
$releaseRoot = Join-Path $repoRoot 'release-work'
$distRoot = Join-Path $releaseRoot 'dist'
$buildRoot = Join-Path $releaseRoot 'build'
$specRoot = Join-Path $releaseRoot 'spec'
$packageDir = Join-Path $distRoot 'CodexPetLive'
$auditScript = Join-Path $scriptDir 'audit_release_package.ps1'
$entryPoint = Join-Path $repoRoot 'CodexPetLive\__main__.py'
$resourceDir = Join-Path $repoRoot 'res'
$settingsFile = Join-Path $repoRoot 'CodexPetLive/settings.py'

function Write-Step {
    param([string] $Message)
    Write-Host "[release] $Message"
}

function Assert-FileExists {
    param(
        [string] $Path,
        [string] $Description
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Description not found: $Path"
    }
}

function Assert-ChildPath {
    param(
        [string] $ChildPath,
        [string] $ParentPath
    )

    $resolvedParent = if (Test-Path -LiteralPath $ParentPath) {
        (Resolve-Path -LiteralPath $ParentPath).Path
    }
    else {
        [System.IO.Path]::GetFullPath($ParentPath)
    }
    $resolvedChild = if (Test-Path -LiteralPath $ChildPath) {
        (Resolve-Path -LiteralPath $ChildPath).Path
    }
    else {
        [System.IO.Path]::GetFullPath($ChildPath)
    }

    $parentWithSeparator = $resolvedParent.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolvedChild.StartsWith($parentWithSeparator, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside release root: $resolvedChild"
    }
}

if ($Configuration -notin @('windowed', 'console')) {
    throw "Unsupported configuration '$Configuration'. Use 'windowed' or 'console'."
}

if ($PythonPath -ne 'python') {
    Assert-FileExists -Path $PythonPath -Description 'Python interpreter'
}
Assert-FileExists -Path $entryPoint -Description 'Application entry point'
Assert-FileExists -Path $auditScript -Description 'Release audit script'
Assert-FileExists -Path $settingsFile -Description 'Application settings file'
if (-not (Test-Path -LiteralPath $resourceDir -PathType Container)) {
    throw "Resource directory not found: $resourceDir"
}

$settingsText = Get-Content -LiteralPath $settingsFile -Raw -Encoding UTF8
$versionMatch = [regex]::Match($settingsText, 'VERSION\s*=\s*"([^"]+)"')
if (-not $versionMatch.Success) {
    throw "Unable to read VERSION from $settingsFile"
}
$appVersion = $versionMatch.Groups[1].Value
if ([string]::IsNullOrWhiteSpace($Version)) {
    $Version = $appVersion
}
if ($Version -ne $appVersion) {
    throw "Release version '$Version' does not match application VERSION '$appVersion'."
}

$safeVersion = $Version -replace '[^A-Za-z0-9_.-]', '-'
$zipPath = Join-Path $releaseRoot "CodexPetLive-$safeVersion-windows-x64.zip"

if (-not $SkipBuild) {
    Write-Step 'Cleaning release-work output directories'
    foreach ($path in @($distRoot, $buildRoot, $specRoot)) {
        if (Test-Path -LiteralPath $path) {
            Assert-ChildPath -ChildPath $path -ParentPath $releaseRoot
            Remove-Item -LiteralPath $path -Recurse -Force
        }
    }
    New-Item -ItemType Directory -Force -Path $distRoot, $buildRoot, $specRoot | Out-Null

    $pyInstallerArgs = @(
        '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--name', 'CodexPetLive',
        '--distpath', $distRoot,
        '--workpath', $buildRoot,
        '--specpath', $specRoot,
        '--add-data', "$resourceDir;res",
        '--hidden-import', 'pynput.mouse._win32',
        '--hidden-import', 'pynput.keyboard._win32',
        '--collect-submodules', 'qfluentwidgets',
        '--collect-data', 'qfluentwidgets'
    )

    if ($Configuration -eq 'windowed') {
        $pyInstallerArgs += '--noconsole'
    }

    $iconPath = Join-Path $repoRoot '000.ico'
    if (Test-Path -LiteralPath $iconPath -PathType Leaf) {
        $pyInstallerArgs += @('--icon', $iconPath)
    }

    $pyInstallerArgs += $entryPoint

    Write-Step "Running PyInstaller with $PythonPath"
    Push-Location $repoRoot
    try {
        & $PythonPath @pyInstallerArgs
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path -LiteralPath $packageDir -PathType Container)) {
    throw "Expected PyInstaller output directory not found: $packageDir"
}

Write-Step 'Auditing unpacked release directory'
& $auditScript -PackagePath $packageDir
if ($LASTEXITCODE -ne 0) {
    throw "Unpacked release audit failed with exit code $LASTEXITCODE."
}

if (-not $SkipArchive) {
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    Write-Step "Creating archive $zipPath"
    Compress-Archive -LiteralPath $packageDir -DestinationPath $zipPath -CompressionLevel Optimal

    Write-Step 'Auditing release archive'
    & $auditScript -PackagePath $zipPath
    if ($LASTEXITCODE -ne 0) {
        throw "Release archive audit failed with exit code $LASTEXITCODE."
    }
}

Write-Step 'Release build completed'
Write-Host "Dist: $distRoot"
if (-not $SkipArchive) {
    Write-Host "Archive: $zipPath"
}
