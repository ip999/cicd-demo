git status
git pull
echo "" >> ../backend/dummy.txt
git add ../backend/dummy.txt
git commit -am "bump"
git push origin main
while true; do curl -s https://box.threatline.io/version; echo ; sleep 5; done