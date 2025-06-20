# scaffold-react.ps1
# Run from your repo root (where logonico-ui was created)

# 1. Validate React src exists
$root     = Split-Path -Parent $MyInvocation.MyCommand.Path
$reactSrc = Join-Path $root 'logonico-ui\src'
if (-not (Test-Path $reactSrc)) {
    Write-Error "ERROR: React src directory not found at $reactSrc. Run this script from project root after CRA."
    exit 1
}

# 2. Create folder structure
$dirs = @(
    'components\common',
    'components\Header',
    'components\Sidebar',
    'components\Gallery',
    'components\SelectionPanel',
    'components\Layout',
    'hooks',
    'services',
    'styles',
    'utils',
    'types'
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path (Join-Path $reactSrc $d) -Force | Out-Null
}

# 3. Create empty placeholder files
$files = @(
    'services\apiService.js',
    'services\imageParser.js',
    'services\themeService.js',
    'services\fileUtils.js',
    'hooks\useImages.js',
    'hooks\useStats.js',
    'hooks\useLogs.js',
    'hooks\useResizePanel.js',
    'hooks\useTheme.js',
    'hooks\useAppState.js',
    'components\common\ImageCard.js',
    'components\common\FilterButton.js',
    'components\common\ActionButton.js',
    'components\common\ProgressBar.js',
    'components\common\StatusBadge.js',
    'components\common\LoadingSpinner.js',
    'components\Gallery\ImageGrid.js',
    'components\Gallery\ProviderDots.js',
    'components\Gallery\LogEntry.js',
    'components\Gallery\SelectionActions.js',
    'components\Gallery\ResizeHandle.js',
    'components\Header\Header.js',
    'components\Sidebar\Sidebar.js',
    'components\Gallery\Gallery.js',
    'components\SelectionPanel\SelectionPanel.js',
    'components\Layout\AppLayout.js',
    'components\Layout\PanelContainer.js'
)
foreach ($f in $files) {
    $path = Join-Path $reactSrc $f
    if (-not (Test-Path $path)) {
        New-Item -ItemType File -Path $path -Force | Out-Null
    }
}

Write-Host '✅ React folder & file scaffold complete.'
