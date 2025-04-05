import bot/context
import bot/database
import discord_gleam
import discord_gleam/ws/packets/message
import gleam/int
import gleam/result
import gleam/string

pub fn claim(
  ctx: context.Context,
  message: message.MessagePacket,
  content: String,
) {
  use guild_id <- result.try(int.parse(message.d.guild_id))
  use uid <- result.try(int.parse(message.d.author.id))
  case string.split(content, " ") {
    [arg, ..] -> {
      use id <- result.try(int.parse(arg))
      use req <- result.try(
        database.claim_request(ctx.db, guild_id, uid, id)
        |> result.map_error(fn(_) { Nil }),
      )
      Ok(
        discord_gleam.send_message(
          ctx.bot,
          message.d.channel_id,
          "<@"
            <> int.to_string(req.requestor_id)
            <> ">"
            <> "\nClaimed by: <@"
            <> message.d.author.id
            <> ">"
            <> "\nID: "
            <> int.to_string(req.id)
            <> "\n"
            <> req.resource_message,
          [],
        ),
      )
    }
    [] -> Error(Nil)
  }
}
