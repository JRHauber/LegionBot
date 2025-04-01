import bot/context
import bot/database
import discord_gleam
import discord_gleam/discord/snowflake
import discord_gleam/ws/packets/message
import gleam/int
import gleam/list
import gleam/result

fn format_message(acc: String, data: List(database.UserRequest)) -> String {
  // needs formatting
  case data {
    [] -> "```\n" <> acc
    [req, ..data] ->
      format_message(
        int.to_string(req.id) <> " - " <> req.resource_message <> "\n" <> acc,
        data,
      )
  }
}

fn send_messages(
  ctx: context.Context,
  channel_id: snowflake.Snowflake,
  data: List(database.UserRequest),
) -> Nil {
  let #(first, second) = list.split(data, 30)

  case first {
    [] -> Nil
    _ -> {
      discord_gleam.send_message(
        ctx.bot,
        channel_id,
        format_message("```", data),
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
