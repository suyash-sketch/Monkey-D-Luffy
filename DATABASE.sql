//Create a database eg.miniproject

CREATE DATABASE miniproject;


//1.Create a table "users"
CREATE TABLE users (
  iduser INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NULL,
  last_name VARCHAR(50) NULL,
  gender VARCHAR(50) NULL,
  birthdate DATE NULL,
  email VARCHAR(50) NULL,
  username VARCHAR(50) NULL,
  password VARCHAR(50) NULL,
  );

//2.create table "accounts"
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(50),
    a_username VARCHAR(50),
    a_password VARCHAR(50),
);

//3.alter the table accounts
ALTER TABLE accounts
ADD COLUMN r_username VARCHAR(255);

ALTER TABLE accounts
ADD CONSTRAINT fk_user
FOREIGN KEY (r_username) REFERENCES users(username)
ON DELETE CASCADE;
