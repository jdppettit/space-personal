DELIMITER ;

DROP TABLE IF EXISTS server;
CREATE TABLE server (
    id INT NOT NULL AUTO_INCREMENT,
    name TINYTEXT NOT NULL,
    disk_size TINYTEXT,
    disk_path TEXT,
    vcupu INT,
    ram INT,
    state TINYINT,
    image TEXT,
    inconsistent TINYINT DEFAULT 0,
    mac_address TINYTEXT,
    PRIMARY KEY (id),
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS image;
CREATE TABLE image (
    id INT NOT NULL AUTO_INCREMENT,
    name TEXT,
    path TEXT,
    size INT,
    PRIMARY KEY (id),
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS log;
CREATE TABLE log (
    id INT NOT NULL AUTO_INCREMENT,
    date DATETTIME DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    level TINYINT,
    PRIMARY KEY (id),
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS event;
CREATE TABLE event (
    id INT NOT NULL AUTO_INCREMENT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    type INT,
    server_id INT NOT NULL,
    PRIMARY KEY (id),
)
ENGINE = InnoDB;

DROP TABLE IF EXISTS ipaddress;
CREATE TABLE ipaddress (
    id INT NOT NULL AUTO_INCREMENT,
    ip TEXT,
    
)
ENGINE = InnoDB;


