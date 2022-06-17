echo "Finished rendering on `date`"
if [ -z $QUARTO_PROJECT_RENDER_ALL+x ] 
then
    echo "Not pushing to git because this is not a full render"
else
    git add .; git commit -m "Rendered on `date`"; git push
fi
