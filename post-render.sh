echo "Finished rendering on `date`"
if [ -z $QUARTO_PROJECT_RENDER_ALL+x ] 
then
    echo "Not pushing to git because this is not a full render"
else
    python3.10 post-articles.py
    python3.10 create_sitemap.py
    git add .; git commit -m "Rendered on `date`"; git push   
    python3.10 submit_sitemap.py

fi
