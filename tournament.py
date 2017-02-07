#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

from __future__ import division, print_function
import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("DELETE FROM matches_participant")
    cur.execute("DELETE FROM matches")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("DELETE FROM players")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""    
    # with connect() as conn:
    #     with conn.cursor() as cur:
    conn = connect()
    cur  = conn.cursor()
    cur.execute("SELECT count(*) FROM players;")
    num_players_from_db = cur.fetchone()
    conn.close()
    return num_players_from_db[0]


def registerPlayer(name):
    """Adds a player to the tournament database.  

    The database assigns a unique serial id number for the player.  
    Args:
      name: the player's full name (need not be unique).
    """    
    conn = connect()
    cur  = conn.cursor()
    cur.execute("INSERT INTO players(name) VALUES(%s)", (name,))
    conn.commit()
    conn.close()

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
    conn = connect()
    cur  = conn.cursor()
    cur.execute('''
        SELECT p.id, p.name, SUM(CASE WHEN p.id=m.winner_id THEN 1 ELSE 0 END) as wins, count(m.id)
        FROM players as p 
            LEFT JOIN matches_participant as mp
                JOIN matches as m
                ON m.id=mp.match_id
            ON p.id=mp.player_id
        GROUP BY p.id
        ORDER BY wins DESC;
        ''')
    standings = cur.fetchall()
    # print()
    # print(standings)
    # print()
    # match_id = cur.fetchone()[0]
    # print(match_id)
    # cur.execute("INSERT INTO matches_participant VALUES(%s, %s);", (match_id, loser ))
    # cur.execute("INSERT INTO matches_participant VALUES(%s, %s);", (match_id, winner))
    # conn.commit()
    conn.close()
    return standings 


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cur  = conn.cursor()
    cur.execute("INSERT INTO matches(winner_id) VALUES(%s) RETURNING id;", (winner,))
    match_id = cur.fetchone()[0]
    # print('match id: ', match_id)
    cur.execute("INSERT INTO matches_participant VALUES(%s, %s);", (match_id, loser ))
    cur.execute("INSERT INTO matches_participant VALUES(%s, %s);", (match_id, winner))
    conn.commit()
    conn.close()
 
 
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


