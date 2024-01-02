# Print that we started the publish process at the current time
$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "Publish started at $now"

git add .
git commit -m "New rendering as of $now"
git push   

# Build the site
quarto publish gh-pages --no-prompt

# python utils/process-articles.py
python utils/create_sitemap.py
python utils/submit_sitemap.py

$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Output "Publish finished at $now"
