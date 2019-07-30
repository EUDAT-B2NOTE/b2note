export SQLDB_NAME='users.sqlite3'
export MONGODB_NAME='b2note_mongodb'
export MONGODB_USR='b2note'
export MONGODB_PWD='b2note'

echo Export users from sqlite
sqlite3 $SQLDB_NAME <<EOT
.headers on
.mode csv
.output userprofiles.csv
SELECT * FROM accounts_annotatorprofile;
.quit
EOT

echo Cleaning mongodb user profiles
mongo -u $MONGODB_USR -p $MONGODB_PWD -d MONGODB_NAME <<EOF
db.userprofile.drop()
db.userstomigrate.drop()
EOF

echo Importing user db to migrate
mongoimport --d $MONGODB_NAME -u $MONGODB_USR -p $MONGODB_PWD --collection userstomigrate --file userprofiles.csv --type csv --headerline

