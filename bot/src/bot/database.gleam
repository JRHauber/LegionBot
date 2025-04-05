import gleam/dynamic/decode
import gleam/option
import gleam/regexp
import gleam/result
import gleam/string
import sqlight

pub type Connection =
  sqlight.Connection

pub fn with_connection(name: String, f: fn(sqlight.Connection) -> a) -> a {
  use conn <- sqlight.with_connection(name)
  let assert Ok(_) = sqlight.exec("pragma foreign_keys = on;", conn)
  f(conn)
}

pub fn migrate_schema(conn: sqlight.Connection) -> Result(Nil, Nil) {
  sqlight.exec(
    "
    CREATE TABLE IF NOT EXISTS requests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      server_id INTEGER NOT NULL,
      filled BOOL NOT NULL,
      requestor_id INTEGER NOT NULL,
      claimant_id INTEGER,
      resource_message VARCHAR(20) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS resources (
      resource_id  INTEGER PRIMARY KEY,
      project_id INTEGER,
      name TEXT NOT NULL,
      total_amount INTEGER NOT NULL,
      UNIQUE(name, project_id) ON CONFLICT ABORT,
      FOREIGN KEY(project_id) REFERENCES projects(project_id)
    );

    CREATE TABLE IF NOT EXISTS contributors (
      contributor_id INTEGER NOT NULL,
      project_id INTEGER NOT NULL,
      PRIMARY KEY(contributor_id, project_id),
      FOREIGN KEY(project_id) REFERENCES projects(project_id)
    );

    CREATE TABLE IF NOT EXISTS contributions (
      resource_id INTEGER,
      contributor_id INTEGER,
      amount INTEGER NOT NULL,
      PRIMARY KEY(resource_id, contributor_id),
      FOREIGN KEY(resource_id) REFERENCES resoruces(resource_id),
      FOREIGN KEY(contributor_id) REFERENCES contributors(contributor_id)
    );

    CREATE TABLE IF NOT EXISTS projects (
      project_id INTEGER PRIMARY KEY AUTOINCREMENT,
      server_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      time INTEGER NOT NULL,
      completed BOOL NOT NULL
    );
    ",
    conn,
  )
  |> result.map_error(fn(_) { Nil })
}

// '[^a-zA-Z0-9 ]+' sub out for nothing
fn sanitize(dirty: String) -> String {
  let assert Ok(re) = regexp.from_string("[^a-zA-Z0-9 ]+")
  regexp.replace(re, dirty, "")
  |> string.slice(0, 30)
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
  let resource_message = sanitize(resource_message)
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
