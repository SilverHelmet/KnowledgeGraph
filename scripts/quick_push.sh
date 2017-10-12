echo '---------------------------'
git pull origin master
echo '---------------------------'
git add *
echo '---------------------------'
git commit -m "$1"
echo '---------------------------'
git push origin master