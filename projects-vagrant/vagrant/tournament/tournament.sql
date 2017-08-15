-- Table definitions for the tournament project.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
	name text,
	played integer DEFAULT 0,
	won integer DEFAULT 0,
	lost integer DEFAULT 0,
	id serial primary key
);

CREATE TABLE matches (
	winner integer,
	loser integer,
	id serial primary key
);

CREATE VIEW ordered_by_wins AS 
	SELECT * FROM players 
	ORDER BY won DESC;