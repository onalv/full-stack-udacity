#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit()

    #set numbers of losses, winnings and games played to zero when matches deleted
    c.execute("UPDATE players SET played = 0, won = 0, lost = 0")
    conn.commit()

    conn.close()
    return 0

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit()
    conn.close()
    return 0

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT count(*) AS num FROM players;")
    count = c.fetchone()[0]
    conn.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
    
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players VALUES (%s)", (name,))
    conn.commit()
    conn.close()
    return 0


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    list_standings = []
    conn = connect()
    c = conn.cursor()

    #get players list orderd by wins with a VIEW created in tournament.sql
    c.execute("SELECT * FROM ordered_by_wins;")
    results = c.fetchall()
    
    #create list as per request with the data from the database
    for row in results:
        list_standings.append((row[4], row[0], row[2], row[1]))

    conn.close()
    return list_standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()

    #add match to matches table
    c.execute("INSERT INTO matches VALUES (%s, %s)", (winner,loser,))
    conn.commit()
    
    #update winnings for winner in players table
    c.execute("SELECT played, won FROM players WHERE id = %s", (winner,))
    result = c.fetchone()
    played = result[0]
    played = played + 1
    won = result[1]
    won = won + 1
    c.execute("UPDATE players SET played = %s, won = %s WHERE id = %s", (played, won, winner,))
    conn.commit()

    #Update losses for loser in players table
    c.execute("SELECT played, lost FROM players WHERE id = %s", (loser,))
    result = c.fetchone()
    played = result[0]
    played = played + 1
    lost = result[1]
    lost = lost + 1
    c.execute("UPDATE players SET played = %s, lost = %s WHERE id = %s", (played, lost, loser,))
    conn.commit()
   
    conn.close()
    return 0
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    conn = connect()
    c = conn.cursor()

    #get players list orderd by wins with a VIEW created in tournament.sql
    c.execute("SELECT * FROM ordered_by_wins")
    results = c.fetchall()
   
    #create the list with the pair of players
    for x in xrange(0, len(results), 2):
        pairings.append((results[x][4], results[x][0], results[x+1][4], results[x+1][0])) 

    return pairings
