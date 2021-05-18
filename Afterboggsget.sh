echo "Do  8.8 updates from 0.8.7"
sudo mysql -e "ALTER TABLE osp.settings ADD COLUMN proxyFQDN VARCHAR(2048) NULL AFTER requireConfirmedEmail"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN rtmpServer INT NULL AFTER totalViewers"

echo "do performance updates to database will fail if already upgraded"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER rtmpServer, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.RecordedVideo ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER originalStreamID, ADD INDEX NupVotes (NupVotes ASC) VISIBLE "
sudo mysql -e "ALTER TABLE osp.Clips ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER published, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.userNotification ADD INDEX timeStamp (timestamp DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.Channel ADD COLUMN Nsubscriptions INT NULL DEFAULT 0 AFTER vanityURL"

echo "install flask verion of redis... THIS IS NEW SH*T AND HAS MAYBE NOT WORKED RIGHT... Maybe it's already installed???  if you are doing something else silly with Redis which Mark does not know about then that's why this does not work or maybe you need something else installed first to make this pip work if it did not ...???"
sudo pip install flask-redis
echo "Hope the pip worked! (lol)..."

echo "Afterboggsget done..."