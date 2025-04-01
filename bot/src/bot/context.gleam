import bot/database
import discord_gleam/types/bot

pub type Context {
  Context(db: database.Connection, bot: bot.Bot)
}
