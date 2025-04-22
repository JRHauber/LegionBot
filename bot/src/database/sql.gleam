import gleam/dynamic/decode
import gleam/option.{type Option}
import pog

/// A row you get from running the `request_complete` query
/// defined in `./src/database/sql/request_complete.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestCompleteRow {
  RequestCompleteRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_complete` query
/// defined in `./src/database/sql/request_complete.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_complete(db, arg_1, arg_2, arg_3) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestCompleteRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "update request
set filled = true
where request_id = $2 and server_id = $1 and claimant_id = $3 and not filled
returning *;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.parameter(pog.int(arg_3))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_get_user` query
/// defined in `./src/database/sql/request_get_user.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestGetUserRow {
  RequestGetUserRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_get_user` query
/// defined in `./src/database/sql/request_get_user.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_get_user(db, arg_1, arg_2) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestGetUserRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "select * from request
where server_id = $1 and requestor_id = $2 and not filled;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_create` query
/// defined in `./src/database/sql/request_create.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestCreateRow {
  RequestCreateRow(request_id: Int)
}

/// Runs the `request_create` query
/// defined in `./src/database/sql/request_create.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_create(db, arg_1, arg_2, arg_3) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    decode.success(RequestCreateRow(request_id:))
  }

  "insert into request
(server_id, requestor_id, resource_message, filled)
values ($1, $2, $3, false)
returning request_id;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.parameter(pog.text(arg_3))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_get_server` query
/// defined in `./src/database/sql/request_get_server.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestGetServerRow {
  RequestGetServerRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_get_server` query
/// defined in `./src/database/sql/request_get_server.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_get_server(db, arg_1) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestGetServerRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "select * from request
where server_id = $1 and not filled;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_unclaim` query
/// defined in `./src/database/sql/request_unclaim.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestUnclaimRow {
  RequestUnclaimRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_unclaim` query
/// defined in `./src/database/sql/request_unclaim.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_unclaim(db, arg_1, arg_2, arg_3) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestUnclaimRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "update request
set claimant_id = null
where request_id = $2 and server_id = $1 and claimant_id = $3 and not filled
returning *;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.parameter(pog.int(arg_3))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_get_claims` query
/// defined in `./src/database/sql/request_get_claims.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestGetClaimsRow {
  RequestGetClaimsRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_get_claims` query
/// defined in `./src/database/sql/request_get_claims.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_get_claims(db, arg_1, arg_2) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestGetClaimsRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "select * from request
where server_id = $1 and claimant_id = $2 and not filled;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.returning(decoder)
  |> pog.execute(db)
}

/// A row you get from running the `request_claim` query
/// defined in `./src/database/sql/request_claim.sql`.
///
/// > 🐿️ This type definition was generated automatically using v3.0.2 of the
/// > [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub type RequestClaimRow {
  RequestClaimRow(
    request_id: Int,
    server_id: Int,
    filled: Bool,
    requestor_id: Int,
    claimant_id: Option(Int),
    resource_message: String,
  )
}

/// Runs the `request_claim` query
/// defined in `./src/database/sql/request_claim.sql`.
///
/// > 🐿️ This function was generated automatically using v3.0.2 of
/// > the [squirrel package](https://github.com/giacomocavalieri/squirrel).
///
pub fn request_claim(db, arg_1, arg_2, arg_3) {
  let decoder = {
    use request_id <- decode.field(0, decode.int)
    use server_id <- decode.field(1, decode.int)
    use filled <- decode.field(2, decode.bool)
    use requestor_id <- decode.field(3, decode.int)
    use claimant_id <- decode.field(4, decode.optional(decode.int))
    use resource_message <- decode.field(5, decode.string)
    decode.success(
      RequestClaimRow(
        request_id:,
        server_id:,
        filled:,
        requestor_id:,
        claimant_id:,
        resource_message:,
      ),
    )
  }

  "update request
set claimant_id = $3
where request_id = $2 and server_id = $1 and claimant_id is null and not filled
returning *;
"
  |> pog.query
  |> pog.parameter(pog.int(arg_1))
  |> pog.parameter(pog.int(arg_2))
  |> pog.parameter(pog.int(arg_3))
  |> pog.returning(decoder)
  |> pog.execute(db)
}
