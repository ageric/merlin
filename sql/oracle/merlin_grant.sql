PROMPT Creating User merlin ...
CREATE USER merlin IDENTIFIED BY merlin DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP;
GRANT CREATE SESSION, RESOURCE, CREATE VIEW, CREATE MATERIALIZED VIEW, CREATE SYNONYM TO merlin;
PROMPT DONE
