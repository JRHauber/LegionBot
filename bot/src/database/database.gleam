import database/sql
import gleam/option.{type Option}
import gleam/regexp
import gleam/result
import gleam/string
import pog

pub type RequestRow {
  RequestRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

pub type SqlError {
  Internal(pog.QueryError)
  External
}

fn unpack_one(returned: Result(pog.Returned(a), _)) -> Result(a, _) {
  let returned = returned |> result.map_error(Internal)

  use data <- result.then(returned)
  case data {
    pog.Returned(1, [row]) -> Ok(row)
    _ -> Error(External)
  }
}

fn unpack_many(
  returned: Result(pog.Returned(a), _),
) -> Result(#(Int, List(a)), _) {
  let returned = returned |> result.map_error(Internal)

  use data <- result.then(returned)
  Ok(#(data.count, data.rows))
}

// '[^a-zA-Z0-9 ]+' sub out for nothing
fn sanitize(dirty: String, length: Int) -> String {
  let assert Ok(re) = regexp.from_string("[^a-zA-Z0-9 ]+")
  dirty
  |> string.slice(0, length)
  |> regexp.replace(re, _, "")
}

pub fn request_complete(
  db: pog.Connection,
  server_id,
  request_id,
  user_id,
) -> Result(_, SqlError) {
  sql.request_complete(db, server_id, request_id, user_id)
  |> unpack_one
}

pub fn request_get_user(
  db: pog.Connection,
  server_id,
  user_id,
) -> Result(_, SqlError) {
  sql.request_get_user(db, server_id, user_id)
  |> unpack_many
}

pub fn request_create(
  db: pog.Connection,
  server_id,
  requestor_id,
  resource_message,
) -> Result(_, SqlError) {
  let resource_message = resource_message |> sanitize(20)
  sql.request_create(db, server_id, requestor_id, resource_message)
  |> unpack_one
}

pub fn request_get_server(db: pog.Connection, server_id) -> Result(_, SqlError) {
  sql.request_get_server(db, server_id)
  |> unpack_many
}

pub fn request_unclaim(
  db: pog.Connection,
  server_id,
  request_id,
  claimant_id,
) -> Result(_, SqlError) {
  sql.request_unclaim(db, server_id, request_id, claimant_id)
  |> unpack_one
}

pub fn request_get_claims(
  db: pog.Connection,
  server_id,
  user_id,
) -> Result(_, SqlError) {
  sql.request_get_claims(db, server_id, user_id)
  |> unpack_many
}

pub fn request_claim(
  db: pog.Connection,
  server_id,
  request_id,
  claimant_id,
) -> Result(_, SqlError) {
  sql.request_claim(db, server_id, request_id, claimant_id)
  |> unpack_one
}
