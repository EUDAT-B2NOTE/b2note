SQLITE_LOCATION=users.sqlite3
echo Export users from sqlite
sqlite3 $SQLITE_LICATION <<EOT
.headers on
.mode csv
.output userprofiles.csv
SELECT * FROM accounts_annotatorprofile;
.quit
EOT

echo Cleaning mongodb user profiles
mongo -u $MONGODB_USER -p $MONGODB_PWD -d MONGODB_NAME <<EOF
db.userprofile.drop()
db.userstomigrate.drop()
EOF

echo Importing user db to migrate
mongoimport --db $MONGODB_NAME --collection userstomigrate --file userprofiles.csv --type csv --headerline

