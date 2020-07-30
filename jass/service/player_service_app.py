# HSLU
#
# Created by Thomas Koller on 12.10.18
#

from flask import Flask
from jass.agents.agent import Agent
from jass.service.player_service_route import players


class PlayerServiceApp(Flask):
    def __init__(self, import_name,
                 static_url_path=None,
                 static_folder='static',
                 static_host=None, host_matching=False,
                 subdomain_matching=False,
                 template_folder='templates',
                 instance_path=None,
                 instance_relative_config=False,
                 root_path=None):
        super(PlayerServiceApp, self).__init__(import_name,
                                               static_url_path=static_url_path,
                                               static_folder=static_folder,
                                               static_host=static_host,
                                               host_matching=host_matching,
                                               subdomain_matching=subdomain_matching,
                                               template_folder=template_folder,
                                               instance_path=instance_path,
                                               instance_relative_config=instance_relative_config,
                                               root_path=root_path)
        self.players = {}
        self.register_blueprint(players)

    def add_player(self, player_name: str, player: Agent):
        self.players[player_name] = player

    def get_player_for_name(self, player_name: str):
        return self.players[player_name] if player_name in self.players else None

    def get_players(self):
        return [name for name in self.players.keys()]
