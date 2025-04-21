CREATE TABLE IF NOT EXISTS request (
    request_id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    filled BOOLEAN NOT NULL,
    requestor_id INTEGER NOT NULL,
    claimant_id INTEGER,
    resource_message VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS project (
    project_id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL,
    p_name VARCHAR(30) NOT NULL,
    p_time TIMESTAMP NOT NULL,
    completed BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS target (
    target_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    t_name VARCHAR(20) NOT NULL,
    target_amount INTEGER NOT NULL,
    UNIQUE(t_name, project_id),
    FOREIGN KEY(project_id) REFERENCES project(project_id)
);

CREATE TABLE IF NOT EXISTS contribution (
    target_id INTEGER NOT NULL,
    contributor_id INTEGER,
    amount INTEGER NOT NULL,
    PRIMARY KEY(target_id, contributor_id),
    FOREIGN KEY(target_id) REFERENCES target(target_id)
);
