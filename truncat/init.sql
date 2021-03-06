CREATE TABLE users (
    ID     INTEGER  PRIMARY KEY AUTOINCREMENT,
    login  TEXT     NOT NULL
                    UNIQUE,
    passw  TEXT     NOT NULL,
    reg_at DATETIME DEFAULT (CURRENT_TIMESTAMP) 
);

CREATE TABLE source (
    truncat   TEXT     UNIQUE
                       NOT NULL,
    input     TEXT     NOT NULL,
    make_at   DATETIME DEFAULT (CURRENT_TIMESTAMP),
    owner     INTEGER  REFERENCES users (ID) ON DELETE SET NULL
                                             ON UPDATE NO ACTION
                       DEFAULT NULL
);

CREATE TABLE log (
    ID     INTEGER  PRIMARY KEY,
    what   TEXT     NOT NULL,
    use_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    who    INTEGER  REFERENCES users (ID) ON DELETE SET NULL
                                          ON UPDATE NO ACTION
                    DEFAULT NULL,
    IP     TEXT     DEFAULT NULL
);

CREATE TABLE message (
    ID          INTEGER  PRIMARY KEY,
    name        STRING   NOT NULL,
    email       STRING   NOT NULL,
    content     TEXT     NOT NULL,
    messaged_at DATETIME DEFAULT (CURRENT_TIMESTAMP) 
);

CREATE TABLE alias (
    ID      TEXT     NOT NULL
                     UNIQUE
                     PRIMARY KEY,
    url     TEXT     REFERENCES source (truncat) ON DELETE SET NULL
                                                 ON UPDATE NO ACTION
                     NOT NULL,
    owner   INTEGER  REFERENCES users (ID) ON DELETE SET NULL
                                           ON UPDATE NO ACTION
                     NOT NULL,
    make_at DATETIME DEFAULT (CURRENT_TIMESTAMP) 
);