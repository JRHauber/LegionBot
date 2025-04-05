import bot/context
import bot/database
import discord_gleam
import discord_gleam/ws/packets/message
import gleam/int
import gleam/result

pub fn request(
  ctx: context.Context,
  message: message.MessagePacket,
  content: String,
) {
  use guild_id <- result.try(int.parse(message.d.guild_id))
  use uid <- result.try(int.parse(message.d.author.id))
  use id <- result.try(
    database.create_request(ctx.db, guild_id, uid, content)
    |> result.map_error(fn(_) { Nil }),
  )
  Ok(
    discord_gleam.send_message(
      ctx.bot,
      message.d.channel_id,
      "<@"
        <> message.d.author.id
        <> ">"
        <> "\nID: "
        <> int.to_string(id)
        <> "\n"
        <> content,
      [],
    ),
  )
}
