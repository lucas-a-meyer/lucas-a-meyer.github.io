Write-Output "Starting post expansion process"
python utils/expand_posts.py
Write-Output "Started publish process"
quarto publish gh-pages
python process-articles.py
python create_sitemap.py
git add .
git commit -m "New rendering"
git push   
python submit_sitemap.py
Write-Output "Publish completed"