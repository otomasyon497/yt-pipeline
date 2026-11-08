# Download the newest finished render of an episode from its private GitHub release.
#   powershell -File tools\fetch_episode.ps1 suez-v3            # download into Videos\yt-pipeline\<slug>
#   powershell -File tools\fetch_episode.ps1 suez-v3 -Delete    # ...and delete the release afterwards
param([Parameter(Mandatory = $true)][string]$Slug, [switch]$Delete)
$repo = "otomasyon497/yt-pipeline"
# Filter in PowerShell: Windows PowerShell 5.1 strips the inner double quotes of a --jq expression on its way to gh.
# ConvertFrom-Json emits a JSON array as one object there, so keep it in a variable and pipe that (one item each).
$releases = gh release list -R $repo --limit 100 --json tagName,createdAt | ConvertFrom-Json
$tag = $releases | Where-Object { $_.tagName -match "^ep-$([regex]::Escape($Slug))-\d+$" } | Sort-Object createdAt | Select-Object -Last 1 -ExpandProperty tagName
if (-not $tag) { Write-Error "No release found for $Slug"; exit 1 }
$dest = Join-Path $env:USERPROFILE "Videos\yt-pipeline\$Slug"
New-Item -ItemType Directory -Force $dest | Out-Null
gh release download $tag -R $repo -D $dest --clobber
Write-Output "Downloaded $tag to $dest"
if ($Delete) { gh release delete $tag -R $repo -y --cleanup-tag; Write-Output "Deleted release $tag" }
