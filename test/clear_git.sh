git branch master
git checkout master
git checkout --orphan latest_branch
git status
git add *
git commit -am "Clear Repo"
git branch -D master
git branch -m master
git push -f origin master
