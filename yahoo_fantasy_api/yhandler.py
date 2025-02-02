#!/bin/python

import json

YAHOO_ENDPOINT = 'https://fantasysports.yahooapis.com/fantasy/v2'


class YHandler:
    """Class that constructs the APIs to send to Yahoo"""

    def __init__(self, sc):
        self.sc = sc

    def get(self, uri):
        """Send an API request to the URI and return the response as JSON

        :param uri: URI of the API to call
        :type uri: str
        :return: JSON document of the response
        :raises: RuntimeError if any response comes back with an error
        """
        response = self.sc.session.get("{}/{}".format(YAHOO_ENDPOINT, uri),
                                       params={'format': 'json'})
        jresp = response.json()
        if "error" in jresp:
            raise RuntimeError(json.dumps(jresp))
        return jresp

    def put(self, uri, data):
        """Calls the PUT method to the uri with a payload

        :param uri: URI of the API to call
        :type uri: str
        :param data: What to pass as the payload
        :type data: str
        :return: XML document of the response
        :raises: RuntimeError if any response comes back with an error
        """
        headers = {'Content-Type': 'application/xml'}
        response = self.sc.session.put("{}/{}".format(YAHOO_ENDPOINT, uri),
                                       data=data, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(response.content)
        return response

    def post(self, uri, data):
        """Calls the POST method to the URI with a payload

        :param uri: URI of the API to call
        :type uri: str
        :param data: What to pass as the payload
        :type data: str
        :return: XML document of the response
        :raises: RuntimeError if any response comes back with an error
        """
        headers = {'Content-Type': 'application/xml'}
        response = self.sc.session.post("{}/{}".format(YAHOO_ENDPOINT, uri),
                                        data=data, headers=headers)
        if response.status_code != 201:
            raise RuntimeError(response.content)
        return response

    def get_teams_raw(self):
        """Return the raw JSON when requesting the logged in players teams.

        :return: JSON document of the request.
        """
        return self.get("users;use_login=1/games/teams")

    def get_standings_raw(self, league_id):
        """Return the raw JSON when requesting standings for a league.

        :param league_id: League ID to get the standings for
        :type league_id: str
        :return: JSON document of the request.
        """
        return self.get("league/{}/standings".format(league_id))

    def get_settings_raw(self, league_id):
        """Return the raw JSON when requesting settings for a league.

        :param league_id: League ID to get the standings for
        :type league_id: str
        :return: JSON document of the request.
        """
        return self.get("league/{}/settings".format(league_id))

    def get_matchup_raw(self, team_key, week):
        """Return the raw JSON when requesting match-ups for a team

        :param team_key: Team key identifier to find the matchups for
        :type team_key: str
        :param week: What week number to request the matchup for?
        :type week: int
        :return: JSON of the request
        """
        return self.get("team/{}/matchups;weeks={}".format(team_key, week))

    def get_roster_raw(self, team_key, week=None, day=None):
        """Return the raw JSON when requesting a team's roster

        Can request a roster for a given week or a given day.  If neither is
        given the current day's roster is returned.

        :param team_key: Team key identifier to find the matchups for
        :type team_key: str
        :param week: What week number to request the roster for?
        :type week: int
        :param day: What day number to request the roster
        :type day: datetime.date
        :return: JSON of the request
        """
        if week is not None:
            param = ";week={}".format(week)
        elif day is not None:
            param = ";date={}".format(day.strftime("%Y-%m-%d"))
        else:
            param = ""
        return self.get("team/{}/roster{}".format(team_key, param))

    def get_scoreboard_raw(self, league_id, week=None):
        """Return the raw JSON when requesting the scoreboard for a week

        :param league_id: League ID to get the standings for
        :type league_id: str
        :param week: The week number to request the scoreboard for
        :type week: int
        :return: JSON document of the request.
        """
        week_uri = ""
        if week is not None:
            week_uri = ";week={}".format(week)
        return self.get("league/{}/scoreboard{}".format(league_id, week_uri))

    def get_players_raw(self, league_id, start, status, position=None):
        """Return the raw JSON when requesting players in the league

        The result is limited to 25 players.

        :param league_id: League ID to get the players for
        :type league_id: str
        :param start: The output is paged at 25 players each time.  Use this
        parameter for subsequent calls to get the players at the next page.
        For example, you specify 0 for the first call, 25 for the second call,
        etc.
        :type start: int
        :param status: A filter to limit the player status.  Available values
        are: 'A' - all available; 'FA' - free agents; 'W' - waivers, 'T' -
        taken players, 'K' - keepers
        :type status: str
        :param position: A filter to return players only for a specific
        position.  If None is passed, then no position filtering occurs.
        :type position: str
        :return: JSON document of the request.
        """
        if position is None:
            pos_parm = ""
        else:
            pos_parm = ";position={}".format(position)
        return self.get(
            "league/{}/players;start={};count=25;status={}{}/percent_owned".
            format(league_id, start, status, pos_parm))

    def get_player_raw(self, league_id, player_name):
        """Return the raw JSON when requesting player details

        :param league_id: League ID to get the player for
        :type league_id: str
        :param player_name: Name of player to get the details for
        :type player_name: str
        :return: JSON document of the request.
        """
        player_stat_uri = ""
        if player_name is not None:
            player_stat_uri = "players;search={}/stats".format(player_name)
        return self.get("league/{}/{}".format(league_id, player_stat_uri))

    def get_percent_owned_raw(self, league_id, player_ids):
        """Return the raw JSON when requesting the percentage owned of players

        :param league_id: League ID we are requesting data from
        :type league_id: str
        :param player_ids: Yahoo! Player IDs to retrieve % owned for
        :type player_ids: list(str)
        :return: JSON document of the request
        """
        lg_pref = league_id[0:league_id.find(".")]
        joined_ids = ",".join([lg_pref + ".p." + str(i) for i in player_ids])
        return self.get(
            "league/{}/players;player_keys={}/percent_owned".
            format(league_id, joined_ids))

    def put_roster(self, team_key, xml):
        """Calls PUT against the roster API passing it an xml document

        :param team_key: The key of the team the roster move applies too
        :type team_key: str
        :param xml: The XML document to send
        :type xml: str
        :return: Response from the PUT
        """
        return self.put("team/{}/roster".format(team_key), xml)

    def post_transactions(self, league_id, xml):
        """Calls POST against the transaction API passing it an xml document

        :param league_id: The league ID that the API request applies to
        :type league_id: str
        :param xml: The XML document to send as the payload
        :type xml: str
        :return: Response from the POST
        """
        return self.post("league/{}/transactions".format(league_id), xml)
