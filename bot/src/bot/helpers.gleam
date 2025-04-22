import discord_gleam
import discord_gleam/discord/snowflake
import discord_gleam/types/bot
import gleam/option

pub fn get_username(
  bot: bot.Bot,
  user_id: snowflake.Snowflake,
) -> option.Option(String) {
  discord_gleam.get_user(bot, user_id)
  |> option.then(fn(user) { option.Some(user.username) })
}
