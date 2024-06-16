DROP TABLE IF EXISTS Client

CREATE TABLE Client
(
	Email varchar(40) PRIMARY KEY NOT NULL,
	Username varchar(20) NOT NULL,
	Password varchar(255) NOT NULL
)

SELECT * FROM Client

INSERT INTO CLIENT (Email, Username, Password)
VALUES('ch@gmail.com', 'ch', 'ch')