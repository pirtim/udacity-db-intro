-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players (
    id serial primary key,
    name text
);

CREATE TABLE matches (
    id serial primary key,
    winner_id integer references players
);

CREATE TABLE matches_participant (
    match_id integer references matches,
    player_id integer references players
);

CREATE VIEW standings AS SELECT p.id AS id, p.name AS name, SUM(CASE WHEN p.id=m.winner_id THEN 1 ELSE 0 END) AS wins, count(m.id) AS matches_played
        FROM players AS p 
            LEFT JOIN matches_participant AS mp
                JOIN matches AS m
                ON m.id=mp.match_id
            ON p.id=mp.player_id
        GROUP BY p.id
        ORDER BY wins DESC;

CREATE VIEW standings_with_id AS SELECT ROW_NUMBER() OVER (ORDER BY wins DESC) AS id_entry, id, name, wins, matches_played FROM standings;