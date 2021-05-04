cd ~/rthk_checker
date >> output.log
python3 main.py >> output.log
git add *
git commit --all -F commitmessage.txt
git push
echo >> output.log
