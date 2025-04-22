import bot/command/claim
import bot/command/claims
import bot/command/complete
import bot/command/request
import bot/command/request_list
import bot/command/requests
import bot/command/unclaim
import bot/command/whois
import bot/context
import discord_gleam
import discord_gleam/discord/intents
import discord_gleam/event_handler
import discord_gleam/types/bot
import discord_gleam/ws/packets/message
import dotenv
import envoy
import gleam/option
import logging
import pog

pub fn main() {
  // load env
  dotenv.config()

  let assert Ok(bot_token) = envoy.get("BOT_TOKEN")
  let assert Ok(bot_id) = envoy.get("BOT_ID")

  let assert Ok(db_host) = envoy.get("PGHOST")
  let assert Ok(db_name) = envoy.get("PGDATABASE")
  let assert Ok(db_user) = envoy.get("USER")
  let assert Ok(db_pass) = envoy.get("PGPASSWORD")

  logging.configure()
  logging.set_level(logging.Info)

  let intents =
    intents.Intents(
      ..intents.empty_intents(),
      message_content: True,
      guild_messages: True,
      guild_members: True,
    )

  let bot = discord_gleam.bot(bot_token, bot_id, intents)

  let db =
    pog.default_config()
    |> pog.host(db_host)
    |> pog.database(db_name)
    |> pog.pool_size(15)
    |> pog.user(db_user)
    |> pog.password(option.Some(db_pass))
    |> pog.connect

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
    // command prefix here:
    "!" <> command -> {
      command_handler(ctx, command, message)
    }
    _ -> Nil
  }
}

fn command_handler(
  ctx: context.Context,
  command: String,
  message: message.MessagePacket,
) -> Nil {
  case command {
    "ping" -> {
      discord_gleam.send_message(ctx.bot, message.d.channel_id, "Pong!", [])
    }
    "request " <> content -> {
      let _ = request.request(ctx, message, content)
      Nil
    }
    "requests" -> {
      let _ = requests.requests(ctx, message)
      Nil
    }
    "requestList" -> {
      let _ = request_list.request_list(ctx, message)
      Nil
    }
    "claim " <> content -> {
      let _ = claim.claim(ctx, message, content)
      Nil
    }
    "unclaim " <> content -> {
      let _ = unclaim.unclaim(ctx, message, content)
      Nil
    }
    "claims" -> {
      let _ = claims.claims(ctx, message)
      Nil
    }
    "complete " <> content -> {
      let _ = complete.complete(ctx, message, content)
      Nil
    }
    "whois " <> content -> {
      let _ = whois.whois(ctx, message, content)
      Nil
    }
    _ -> Nil
  }
}
