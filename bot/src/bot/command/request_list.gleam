import bot/context
import bot/database
import bot/helpers
import discord_gleam
import discord_gleam/discord/snowflake
import discord_gleam/ws/packets/message
import gleam/int
import gleam/list
import gleam/option
import gleam/result

fn format_message(
  ctx: context.Context,
  acc: String,
  data: List(database.UserRequest),
) -> String {
  // needs formatting
  case data {
    [] -> "```\n" <> acc
    [req, ..data] -> {
      let requestor =
        req.requestor_id
        |> int.to_string
        |> helpers.get_username(ctx.bot, _)
        |> option.unwrap("Unknown User")

      let claimant =
        req.claimant_id
        |> option.then(fn(id) {
          id
          |> int.to_string
          |> helpers.get_username(ctx.bot, _)
          |> option.or(option.Some("Unknown User"))
        })
        |> option.unwrap("Unclaimed")

      format_message(
        ctx,
        int.to_string(req.id)
          <> " - "
          <> requestor
          <> " - "
          <> claimant
          <> " - "
          <> req.resource_message
          <> "\n"
          <> acc,
        data,
      )
    }
  }
}

fn send_messages(
  ctx: context.Context,
  channel_id: snowflake.Snowflake,
  data: List(database.UserRequest),
) -> Nil {
  let #(first, second) = list.split(data, 15)

  case first {
    [] -> Nil
    _ -> {
      discord_gleam.send_message(
        ctx.bot,
        channel_id,
        format_message(ctx, "```", data),
        [],
      )
      send_messages(ctx, channel_id, second)
    }
  }
}

pub fn request_list(ctx: context.Context, message: message.MessagePacket) {
  use guild_id <- result.try(int.parse(message.d.guild_id))
  use requests <- result.try(
    database.get_requests(ctx.db, guild_id)
    |> result.map_error(fn(_) { Nil }),
  )
  Ok(send_messages(ctx, message.d.channel_id, requests))
}
