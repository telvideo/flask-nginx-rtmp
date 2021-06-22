echo "Do  8.8 updates from 0.8.7"
sudo mysql -e "ALTER TABLE osp.settings ADD COLUMN proxyFQDN VARCHAR(2048) NULL AFTER requireConfirmedEmail"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN rtmpServer INT NULL AFTER totalViewers"

echo "do performance updates to database these will fail if already upgraded"
sudo mysql -e "ALTER TABLE osp.Stream ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER rtmpServer, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.RecordedVideo ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER originalStreamID, ADD INDEX NupVotes (NupVotes ASC) VISIBLE "
sudo mysql -e "ALTER TABLE osp.Clips ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER published, ADD INDEX NupVotes (NupVotes ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.userNotification ADD INDEX timeStamp (timestamp DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.Channel ADD COLUMN Nsubscriptions INT NULL DEFAULT 0 AFTER vanityURL"
sudo mysql -e "ALTER TABLE osp.user ADD COLUMN verified INT NULL DEFAULT 0 AFTER xmppToken"
sudo mysql -e "ALTER TABLE osp.videoComments ADD COLUMN NupVotes INT NULL DEFAULT 0 AFTER videoID"
sudo mysql -e "ALTER TABLE osp.topics ADD INDEX name (name ASC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.Channel ADD COLUMN chatLinks TINYINT(1) NULL DEFAULT 1 AFTER Nsubscriptions"
sudo mysql -e "ALTER TABLE osp.Stream ADD INDEX currentViewers (currentViewers DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.Stream DROP INDEX NupVotes, ADD INDEX NupVotes (NupVotes DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.RecordedVideo ADD INDEX date (videoDate DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.RecordedVideo DROP INDEX NupVotes , ADD INDEX NupVotes (NupVotes DESC) VISIBLE"
sudo mysql -e "ALTER TABLE osp.Channel ADD COLUMN notificationsLastSentTime DATETIME NULL DEFAULT '2021-02-28 07:19:38' AFTER chatLinks"

apt install python3-pip

echo "install flask verion of redis... THIS IS NEW SH*T AND HAS MAYBE NOT WORKED RIGHT... Maybe it's already installed???  if you are doing something else silly with Redis which Mark does not know about then that's why this does not work or maybe you need something else installed first to make these pips work if they did not ...???"
pip install flask-redis
echo "install pottery which is used to critical section startup"
pip3 install pottery
echo "Hope the pips worked! (lol)..."

echo "Aftergitgsget done."