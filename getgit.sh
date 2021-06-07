echo "--------------------------------------------------------"
echo "Get latest code"
echo "-------------------------------------------------------"
sudo systemctl stop osp.target 
echo "OSP Stopped."

echo "Save config.py in /opt and delete OSP directory... "
sudo cp /opt/osp/conf/config.py /opt
sudo rm -r /opt/osp

echo "Getting code from Gitlab..."

git clone https://gitlab.com/markboggs/flask-nginx-rtmp-manager.git /opt/osp
echo "Cloned."

sudo chown -R "www-data:www-data" /opt/osp
echo "Chowned."
echo "Replace config.py"
sudo cp /opt/config.py /opt/osp/conf/config.py

echo "Do aftergitget.sh"
bash /opt/osp/aftergitget.sh

echo "Restart OSP..."
sudo systemctl restart osp.target 
echo "Copy possibly new gitget to /opt"
sudo cp /opt/osp/gitget.sh /opt 
#sudo rm /opt/osp/boggsget
#sudo rm /opt/osp/aftergitget.sh

echo "getgitcomplete."