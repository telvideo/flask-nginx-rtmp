echo "Do  8.8 updates from 0.8.7"
sudo mysql -e "ALTER TABLE osp.settings ADD COLUMN proxyFQDN VARCHAR(2048) NULL AFTER requireConfirmedEmail"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN rtmpServer INT NULL AFTER totalViewers"

echo "do performance updates to database will fail if already upgraded"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER rtmpServer, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.RecordedVideo ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER originalStreamID, ADD INDEX NupVotes (NupVotes ASC) VISIBLE "
sudo mysql -e "ALTER TABLE osp.Clips ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER published, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.userNotification ADD INDEX timeStamp (timestamp DESC) VISIBLE"

echo "Afterboggsget done..."