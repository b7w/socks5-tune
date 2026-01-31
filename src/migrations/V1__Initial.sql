-- Profile
CREATE TABLE profile
(
    id   BIGSERIAL    NOT NULL,
    type VARCHAR(16)  NOT NULL,
    name VARCHAR(255) NOT NULL,
    body VARCHAR(32000),
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX profile_name_idx_u ON profile (name);


-- Proxy
CREATE TABLE proxy
(
    id   BIGSERIAL    NOT NULL,
    name VARCHAR(255) NOT NULL,
    uri  VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);


--- Domain
CREATE TABLE domain
(
    id         BIGSERIAL    NOT NULL,
    profile_id BIGINT       NOT NULL,
    proxy_id   BIGINT       NOT NULL,
    name       VARCHAR(255) NOT NULL,
    wildcard   BOOLEAN      NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (profile_id) REFERENCES profile (id),
    FOREIGN KEY (proxy_id) REFERENCES proxy (id)
);

CREATE INDEX domain_profile_id_idx ON domain (name);
