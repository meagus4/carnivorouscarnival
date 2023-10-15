-- you can "win" negative tickets lol
CREATE TABLE ticket_wins (
  user TEXT NOT NULL, -- or INTEGER since iirc d.py stores user ids as ints for some ungodly reason???
  game TEXT NOT NULL, -- maybe linked with game table if needed? probably not, unless we want to associate some data with the game we _need_ in the DB
  ticket_change INTEGER NOT NULL
);

CREATE TABLE web_game_sessions (
  session_token TEXT NOT NULL UNIQUE, --jwt
  user TEXT NOT NULL,
  game TEXT NOT NULL,
  points INT,
  status INT NOT NULL, -- 0 = not started, 1 = started, 2 = finished
  time_issued datetime not null default CURRENT_TIMESTAMP,
  time_played datetime,
  time_finished datetime
);

CREATE TABLE prize_wins (
  user TEXT NOT NULL,
  game TEXT NOT NULL,
  prize INTEGER NOT NULL
);

create table consumed_tokens (
    token_type TEXT NOT NULL, --Public, Private
    user TEXT NOT NULL,
    game TEXT NOT NULL,
    token_change INTEGER NOT NULL,
    datetime datetime not null default CURRENT_TIMESTAMP
);

CREATE TABLE prizes (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  rarity INTEGER NOT NULL, -- maybe?
  image TEXT -- maybe?
);