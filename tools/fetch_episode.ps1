# Download the newest finished render of an episode from its private GitHub release.
#   powershell -File tools\fetch_episode.ps1 suez-v3            # download into Videos\yt-pipeline\<slug>
#   powershell -File tools\fetch_episode.ps1 suez-v3 -Delete    # ...and delete the release afterwards
param([Parameter(Mandatory = $true)][string]$Slug, [switch]$Delete)
$repo = "otomasyon497/yt-pipeline"
$tag = gh release list -R $repo --limit 100 --json tagName,createdAt --jq "[.[] | select(.tagName | startswith(`"ep-$Slug-`"))] | sort_by(.createdAt) | last | .tagName"
if (-not $tag) { Write-Error "No release found for $Slug"; exit 1 }
$dest = Join-Path $env:USERPROFILE "Videos\yt-pipeline\$Slug"
New-Item -ItemType Directory -Force $dest | Out-Null
gh release download $tag -R $repo -D $dest --clobber
Write-Output "Downloaded $tag to $dest"
if ($Delete) { gh release delete $tag -R $repo -y --cleanup-tag; Write-Output "Deleted release $tag" }
