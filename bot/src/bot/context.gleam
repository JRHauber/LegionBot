import discord_gleam/types/bot
import pog

pub type Context {
  Context(db: pog.Connection, bot: bot.Bot)
}
