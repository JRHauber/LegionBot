import bot/context
import discord_gleam
import discord_gleam/ws/packets/message
import gleam/option
import gleam/string

pub fn whois(
  ctx: context.Context,
  message: message.MessagePacket,
  content: String,
) {
  case string.split(content, " ") {
    [user_id] -> {
      let return_message = case discord_gleam.get_user(ctx.bot, user_id) {
        option.Some(user) -> user.username
        option.None -> "Could not find user with id: " <> user_id
      }

      discord_gleam.send_message(
        ctx.bot,
        message.d.channel_id,
        return_message,
        [],
      )

      Ok(Nil)
    }
    _ -> {
      discord_gleam.send_message(
        ctx.bot,
        message.d.channel_id,
        "Expected exactly one argument",
        [],
      )
      Error("Failure")
    }
  }
}
