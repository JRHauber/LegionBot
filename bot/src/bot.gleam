import bot/command/claim
import bot/command/claims
import bot/command/complete
import bot/command/request
import bot/command/request_list
import bot/command/requests
import bot/command/unclaim
import bot/context
import bot/database
import discord_gleam
import discord_gleam/discord/intents
import discord_gleam/event_handler
import discord_gleam/types/bot
import discord_gleam/ws/packets/message
import dotenv
import envoy
import logging

const db_name = "bot.sqlite3"

pub fn main() {
  dotenv.config()
  // this should load .env file

  let assert Ok(bot_token) = envoy.get("BOT_TOKEN")
  let assert Ok(bot_id) = envoy.get("BOT_ID")

  logging.configure()
  logging.set_level(logging.Info)

  let intents = intents.Intents(message_content: True, guild_messages: True)
  let bot = discord_gleam.bot(bot_token, bot_id, intents)

  use db <- database.with_connection(db_name)
  let assert Ok(_) = database.migrate_schema(db)

  let bot_handler = fn(bot: bot.Bot, event: event_handler.Packet) {
    let ctx = context.Context(db:, bot:)
    event_handler(ctx, event)
  }

  discord_gleam.run(bot, [bot_handler])
}

fn event_handler(ctx: context.Context, packet: event_handler.Packet) {
  case packet {
    event_handler.ReadyPacket(ready) -> {
      logging.log(logging.Info, "Logged in as " <> ready.d.user.username)

      Nil
    }
    event_handler.MessagePacket(message)
      if message.d.author.id != ctx.bot.client_id
    -> {
      logging.log(logging.Info, "Message: " <> message.d.content)
      message_handler(ctx, message)
    }
    _ -> Nil
  }
}

fn message_handler(ctx: context.Context, message: message.MessagePacket) -> Nil {
  case message.d.content {
    "!ping" -> {
      discord_gleam.send_message(ctx.bot, message.d.channel_id, "Pong!", [])
    }
    "!request " <> content -> {
      let _ = request.request(ctx, message, content)
      Nil
    }
    "!requests" -> {
      let _ = requests.requests(ctx, message)
      Nil
    }
    "!requestList" -> {
      let _ = request_list.request_list(ctx, message)
      Nil
    }
    "!claim " <> content -> {
      let _ = claim.claim(ctx, message, content)
      Nil
    }
    "!unclaim " <> content -> {
      let _ = unclaim.unclaim(ctx, message, content)
      Nil
    }
    "!claims" -> {
      let _ = claims.claims(ctx, message)
      Nil
    }
    "!complete " <> content -> {
      let _ = complete.complete(ctx, message, content)
      Nil
    }
    _ -> Nil
  }
}
