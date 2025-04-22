// todo: this file should be swapped for squirrel generated pog queries

import gleam/dynamic/decode
import gleam/option
import gleam/regexp
import gleam/string
import sqlight

pub type Connection =
  sqlight.Connection

pub fn with_connection(name: String, f: fn(sqlight.Connection) -> a) -> a {
  use conn <- sqlight.with_connection(name)
  let assert Ok(_) = sqlight.exec("pragma foreign_keys = on;", conn)
  f(conn)
}

pub fn migrate_schema(conn: sqlight.Connection) -> Result(Nil, _) {
  sqlight.exec(
    // rename plural tables to singular
    "
    CREATE TABLE IF NOT EXISTS requests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      server_id INTEGER NOT NULL,
      filled BOOL NOT NULL,
      requestor_id INTEGER NOT NULL,
      claimant_id INTEGER,
      resource_message VARCHAR(20) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS project (
      project_id INTEGER PRIMARY KEY AUTOINCREMENT,
      server_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      time INTEGER NOT NULL,
      completed BOOL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS target (
      target_id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      target_amount INTEGER NOT NULL,
      UNIQUE(name, project_id) ON CONFLICT ABORT,
      FOREIGN KEY(project_id) REFERENCES projects(project_id)
    );

    CREATE TABLE IF NOT EXISTS contribution (
      target_id INTEGER NOT NULL,
      contributor_id INTEGER,
      amount INTEGER NOT NULL,
      PRIMARY KEY(target_id, contributor_id),
      FOREIGN KEY(target_id) REFERENCES target(target_id)
    );
    ",
    conn,
  )
}

// '[^a-zA-Z0-9 ]+' sub out for nothing
fn sanitize(dirty: String, length: Int) -> String {
  let assert Ok(re) = regexp.from_string("[^a-zA-Z0-9 ]+")
  dirty
  |> string.slice(0, length)
  |> regexp.replace(re, _, "")
}

pub type UserRequest {
  UserRequest(
    id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: option.Option(Int),
    resource_message: String,
  )
}

fn request_decoder() {
  {
    use id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(
      2,
      decode.one_of(decode.bool, [decode.int |> decode.map(fn(n) { n != 0 })]),
    )
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(UserRequest(
      id:,
      server_id:,
      filled:,
      requestor_id:,
      claimant_id:,
      resource_message:,
    ))
  }
}

pub fn create_request(
  conn: Connection,
  server_id: Int,
  requestor_id: Int,
  resource_message: String,
) {
  let resource_message = sanitize(resource_message, 30)
  let sql =
    "INSERT INTO requests
    (server_id, requestor_id, resource_message, filled)
    VALUES (?, ?, ?, FALSE)
    RETURNING id;"
  let decoder = {
    use id <- decode.field(0, decode.int)
    decode.success(id)
  }
  let result =
    sqlight.query(
      sql,
      conn,
      [
        sqlight.int(server_id),
        sqlight.int(requestor_id),
        sqlight.text(resource_message),
      ],
      decoder,
    )

  case result {
    Ok([id]) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
    _ -> Error("Return Error: Result contained more than one value")
  }
}

pub fn claim_request(
  conn: Connection,
  server_id: Int,
  claimant_id: Int,
  id: Int,
) {
  let sql =
    "UPDATE requests
    SET claimant_id = ?
    WHERE id = ? AND server_id = ? AND claimant_id IS NULL AND not filled
    RETURNING *;"
  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(claimant_id), sqlight.int(id), sqlight.int(server_id)],
      request_decoder(),
    )

  case result {
    Ok([req]) -> Ok(req)
    Error(_) -> Error("Sqlite Error")
    _ -> Error("Return Error: Result contained more than one value")
  }
}

pub fn complete_request(
  conn: Connection,
  server_id: Int,
  claimant_id: Int,
  id: Int,
) {
  let sql =
    "UPDATE requests
    SET filled = TRUE
    WHERE id = ? AND server_id = ? AND claimant_id = ? AND not filled
    RETURNING *;"
  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(id), sqlight.int(server_id), sqlight.int(claimant_id)],
      request_decoder(),
    )

  case result {
    Ok([req]) -> Ok(req)
    Error(_) -> Error("Sqlite Error")
    _ -> Error("Return Error: Result contained more than one value")
  }
}

pub fn unclaim_request(
  conn: Connection,
  server_id: Int,
  claimant_id: Int,
  id: Int,
) {
  let sql =
    "UPDATE requests
    SET claimant_id = NULL
    WHERE id = ? AND server_id = ? AND claimant_id = ? AND not filled
    RETURNING *;"
  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(id), sqlight.int(server_id), sqlight.int(claimant_id)],
      request_decoder(),
    )

  case result {
    Ok([req]) -> Ok(req)
    Error(_) -> Error("Sqlite Error")
    _ -> Error("Return Error: Result contained more than one value")
  }
}

pub fn get_claims(conn: Connection, server_id: Int, uid: Int) {
  let sql =
    "SELECT * FROM REQUESTS
    WHERE server_id = ? AND claimant_id = ? AND not filled;"
  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(uid)],
      request_decoder(),
    )

  case result {
    Ok(a) -> Ok(a)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn get_user_requests(conn: Connection, server_id: Int, uid: Int) {
  let sql =
    "SELECT * FROM REQUESTS
    WHERE server_id = ? AND requestor_id = ? AND not filled;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(uid)],
      request_decoder(),
    )

  case result {
    Ok(a) -> Ok(a)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn get_requests(conn: Connection, server_id: Int) {
  let sql =
    "SELECT * FROM REQUESTS
    WHERE not filled AND server_id = ?;"

  let result =
    sqlight.query(sql, conn, [sqlight.int(server_id)], request_decoder())

  case result {
    Ok(a) -> Ok(a)
    Error(_) -> Error("Sqlite Error")
  }
}

// todo
pub fn new_project(conn: Connection, server_id: Int, name: String, time: Int) {
  let name = sanitize(name, 30)

  let sql =
    "INSERT INTO projects
    (server_id, name, time, completed)
    VALUES (?, ?, ?, FALSE)
    RETURNING project_id;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.text(name), sqlight.int(time)],
      decode.int,
    )

  case result {
    Ok(id) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn add_target(
  conn: Connection,
  target: String,
  amount: Int,
  pid: Int,
  server_id: Int,
) {
  let target = sanitize(target, 30)
  // [tx]
  // insert and fail due to f-key
  // add to resources if project not completed
  let sql =
    "
    BEGIN TRANSACTION;

    SELECT
      CASE WHEN server_id = ?
        THEN 1
        ELSE RAISE(ABORT, 'server mismatch')
        END
      FROM project JOIN target ON project.project_id = target.project_id
      WHERE target.project_id = ?;

    INSERT INTO target
      (project_id, name, target_amount)
      VALUES (?, ?, ?);

    COMMIT;"

  let result =
    sqlight.query(
      sql,
      conn,
      [
        sqlight.int(server_id),
        sqlight.int(pid),
        sqlight.int(pid),
        sqlight.text(target),
        sqlight.int(amount),
      ],
      decode.int,
    )

  case result {
    Ok(id) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn remove_target(conn: Connection, target: String, pid: Int, server_id: Int) {
  let target = sanitize(target, 30)
  // join delete
  // delete from resources if project not completed
  let sql =
    "DELETE target FROM
    project as p JOIN target ON project.project_id = target.project_id
    WHERE server_id = ? AND target.project_id = ? AND target.name = ?"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid), sqlight.text(target)],
      decode.int,
    )

  case result {
    Ok(data) -> Ok(data)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn list_projects(conn: Connection, server_id: Int) {
  let sql =
    "SELECT name, project_id FROM project
    WHERE server_id = ? AND NOT completed;"

  let result = sqlight.query(sql, conn, [sqlight.int(server_id)], decode.int)

  case result {
    Ok(data) -> Ok(data)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn list_contributors(conn: Connection, server_id: Int, pid: Int) {
  // do via join projects and contributors
  let sql =
    "SELECT DISTINCT c.contributor_id
    FROM project as p
    JOIN target as t ON p.project_id = t.project_id
    JOIN contribution as c ON t.target_id = c.target_id
    WHERE p.server_id = ? AND c.project_id = ?;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid)],
      decode.int,
    )

  case result {
    Ok(data) -> Ok(data)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn list_contributions(conn: Connection, server_id: Int, pid: Int) {
  // do via join projects, contributors, and resources
  let sql =
    "SELECT c.contributor_id, t.name, c.amount
    FROM projects as p
    JOIN target as t ON p.project_id = t.project_id
    JOIN contribution as c ON t.target_id = c.target_id
    WHERE p.server_id = ? AND c.project_id = ?
    ORDER BY t.name ASC, c.amount DESC;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid)],
      decode.int,
    )

  case result {
    Ok(data) -> Ok(data)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn list_targets(conn: Connection, server_id: Int, pid: Int) {
  // do via join projects and resources
  let sql =
    "SELECT t.name, COALESCE(SUM(c.amount), 0), target_amount
    FROM projects as p
    JOIN target as t ON p.project_id = t.project_id
    JOIN contribution as c ON t.target_id = c.target_id
    WHERE p.server_id = ? AND c.project_id = ?
    ORDER BY t.name ASC, c.amount DESC;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid)],
      decode.int,
    )

  case result {
    Ok(id) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn contribute(
  conn: Connection,
  pid: Int,
  name: String,
  amount: Int,
  uid: Int,
  server_id: Int,
) {
  // add to contributions if target exists in server exists
  // update failover to add
  let sql =
    "BEGIN TRANSACTION;

    SELECT
    CASE WHEN server_id = ?
      THEN 1
      ELSE RAISE(ABORT, 'server mismatch')
      END
    FROM project JOIN target ON project.project_id = target.project_id
    WHERE target.project_id = ?;

    INSERT INTO contribution
      (target_id, contributor_id, amount)
      VALUES (?, ?, ?)
      ON CONFLICT(target_id, contributor_id)
        DO UPDATE SET amount = excluded.amount + amount;

    COMMIT;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid)],
      decode.int,
    )

  case result {
    Ok(id) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
  }
}

pub fn complete_project(conn: Connection, server_id: Int, pid: Int) {
  // update projects to completed if server matches
  let sql =
    "UPDATE project
    SET completed = TRUE
    WHERE project_id = ? AND server_id = ?
    RETURNING name;"

  let result =
    sqlight.query(
      sql,
      conn,
      [sqlight.int(server_id), sqlight.int(pid)],
      decode.int,
    )

  case result {
    Ok(id) -> Ok(id)
    Error(_) -> Error("Sqlite Error")
  }
}
