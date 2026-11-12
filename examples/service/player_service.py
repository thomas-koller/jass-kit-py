# HSLU
#
# Created by Thomas Koller on 7/30/2020
#
"""
Example how to use flask to create a service for one or more players
"""
import logging

from jass.service.player_service_app import PlayerServiceApp
from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.agents.mcts.agent_determinization_mcts import AgentDeterminizationMCTS
from jass.agents.trump.trump_model import TrumpModel, default_model_path


def create_app():
    """
    This is the factory method for flask. It is automatically detected when flask is run, but we must tell flask
    what python file to use:

        export FLASK_APP=player_service.py
        export FLASK_ENV=development
        flask run --host=0.0.0.0 --port=8888
    """
    logging.basicConfig(level=logging.DEBUG)

    # create and configure the app
    app = PlayerServiceApp('player_service')

    # you could use a configuration file to load additional variables
    # app.config.from_pyfile('my_player_service.cfg', silent=False)

    # add some players
    app.add_player('random', AgentRandomSchieber())
    app.add_player('rule_based', AgentRuleBasedSchieber())
    app.add_player('mcts', AgentDeterminizationMCTS(time_budget=4.0))
    app.add_player('mcts_ml', AgentDeterminizationMCTS(time_budget=4.0, trump_model=load_trump_model()))

    return app


def load_trump_model():
    """The trained trump model, or None (rule based trump) if it cannot be loaded, so the service always starts."""
    try:
        return TrumpModel.load()
    except Exception:
        logging.getLogger(__name__).warning('No trump model at %s, mcts_ml selects trump rule based',
                                            default_model_path(), exc_info=True)
        return None


if __name__ == '__main__':
   app = create_app()
   app.run()

