CREATE TABLE Users (
user_id int primary key,
username text,
password text
);

CREATE TABLE Admins (
admin_id int primary key,
username text
);

CREATE TABLE apiusage( -- probably will send me the param of time and api type, which is why i'm just using ApiName text as primary key,
                       -- then we'll return the table as json with all the data inside, probably make the chart/display accordingly with that object...?
ApiName text primary_key, --not sure if i should change this to API key and make a new table to map API to keys instead
user_id int,
Time Datetime,
foreign key(user_id) references users (user_id)
);
