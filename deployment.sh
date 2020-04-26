python3 manage.py migrate
echo ""|sudo -S systemctl restart settle.service
echo ""|sudo -S systemctl restart nginx.service 
