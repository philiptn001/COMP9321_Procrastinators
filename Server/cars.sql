CREATE TABLE Users (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
username text,
password text
);
CREATE TABLE Admins (
admin_id int primary key,
username text
);
CREATE TABLE apiusage(  //backup system for api usage if monittoring board doesn't work
ApiName text primary_key,
user_id int,
Time Datetime,
foreign key(user_id) references users (user_id)
);
