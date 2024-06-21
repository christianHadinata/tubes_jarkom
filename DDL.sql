DROP TABLE IF EXISTS Client

CREATE TABLE Client
(
	Email varchar(255) PRIMARY KEY NOT NULL,
	Username varchar(255) NOT NULL,
	Password varchar(255) NOT NULL
)

SELECT * FROM Client