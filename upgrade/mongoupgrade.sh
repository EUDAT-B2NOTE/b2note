echo Export users from sqlite
sqlite3 users.sqlite3 <<EOT
.headers on
.mode csv
.output userprofiles.csv
SELECT * FROM accounts_annotatorprofile;
.quit
EOT

echo Cleaning mongodb user profiles
mongo <<EOF
use b2notedb
db.userprofile.drop()
db.userstomigrate.drop()
EOF

echo Importing user db to migrate
mongoimport --db b2notedb --collection userstomigrate --file userprofiles.csv --type csv --headerline

