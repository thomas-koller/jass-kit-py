# HSLU
#
# Created by Thomas Koller on 03.08.20
#
import argparse
import json
import os
import logging

from jass.game.const import PUSH
from jass.game.rule_schieber import RuleSchieber
from jass.logs.log_entry_file_generator import LogEntryFileGenerator

from jass.game.game_state_util import state_from_complete_game, observation_from_state, state_for_trump_from_complete_game
from jass.logs.game_log_entry import GameLogEntry
from jass.logs.game_obs_action_log_entry import GameObsActionLogEntry

"""
Tool for converting files that contain complete games into files that contain observations (features) 
and log (action)

"""


def generate_logs(files, output: str, output_dir: str, max_entries_per_file: int, shuffle: bool):
    """
    Create log files containing observation and action for each card played in all the games of
    the input file.

    Args:
        files: input files to convert
        output: base output file name
        output_dir: output directory
        max_entries_per_file: maximal number of entries in a file
        shuffle: shuffle entries before writing

    Returns:

    """
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.join(output_dir, output)

    logger = logging.getLogger(__name__)

    nr_entries_read = 0
    nr_entries_written = 0
    # Generator will split the output into files

    rule_debug = RuleSchieber()

    with LogEntryFileGenerator(basename, max_entries=max_entries_per_file, shuffle=shuffle) as generator:
        #
        # read all files
        #
        for filename in files:
            logger.info('Reading file: {}'.format(filename))
            if not os.path.isfile(filename):
                logger.error('File not found: {}'.format(filename))
                raise ValueError('File not found')
            #
            # read all entries from file and process them
            #
            with open(filename, mode='r') as file:
                for line in file:
                    line_dict = json.loads(line)
                    entry_game_log = GameLogEntry.from_json(line_dict)
                    nr_entries_read += 1
                    #
                    # create entry for each play in the game
                    #
                    game = entry_game_log.game
                    for card in range(36):
                        state = state_from_complete_game(game, cards_played=card)
                        rule_debug.assert_invariants(state)

                        obs = observation_from_state(state, state.player)
                        action = game.get_card_played(card)
                        if action == -1:
                            raise Exception('Illegal action found')
                        entry_obs = GameObsActionLogEntry(obs=obs,
                                                          action=action,
                                                          date=entry_game_log.date,
                                                          player_id=entry_game_log.player_ids[state.player])
                        generator.add_entry(entry_obs.to_json())
                        nr_entries_written += 1
    print('Entries read: {}'.format(nr_entries_read))
    print('Entries written: {}'.format(nr_entries_written))


def generate_logs_trump(files, output: str, output_dir: str, max_entries_per_file: int, shuffle: bool):
    """
    Create log files containing observation and action for each trump selection in all the games of
    the input file.
    Args:
        files: input files to convert
        output: base output file name
        output_dir: output directory
        max_entries_per_file: maximal number of entries in a file
        shuffle: shuffle entries before writing

    Returns:

    """
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.join(output_dir, output)

    logger = logging.getLogger(__name__)

    nr_entries_read = 0
    nr_entries_written = 0
    # Generator will split the output into files

    with LogEntryFileGenerator(basename, max_entries=max_entries_per_file, shuffle=shuffle) as generator:
        #
        # read all files
        #
        for filename in files:
            logger.info('Reading file: {}'.format(filename))
            #
            # read all entries from file and process them
            #
            with open(filename, mode='r') as file:
                for line in file:
                    line_dict = json.loads(line)
                    entry_game_log = GameLogEntry.from_json(line_dict)
                    nr_entries_read += 1
                    #
                    # create entry for each trump selection
                    #
                    state = state_for_trump_from_complete_game(entry_game_log.game, for_forhand=True)
                    obs = observation_from_state(state, state.player)
                    if entry_game_log.game.forehand == 1:
                        action = entry_game_log.game.trump
                    else:
                        action = PUSH
                    entry_obs = GameObsActionLogEntry(obs=obs,
                                                      action=action,
                                                      date=entry_game_log.date,
                                                      player_id=entry_game_log.player_ids[state.player])
                    generator.add_entry(entry_obs.to_json())
                    nr_entries_written += 1

                    if action == PUSH:
                        # add entry for rearhand trump selection
                        state = state_for_trump_from_complete_game(entry_game_log.game, for_forhand=False)
                        obs = observation_from_state(state, state.player)
                        entry_obs = GameObsActionLogEntry(obs=obs,
                                                          action=entry_game_log.game.trump,
                                                          date=entry_game_log.date,
                                                          player_id=entry_game_log.player_ids[state.player])
                        generator.add_entry(entry_obs.to_json())
                        nr_entries_written += 1

    print('Entries read: {}'.format(nr_entries_read))
    print('Entries written: {}'.format(nr_entries_written))


def main():
    parser = argparse.ArgumentParser(description='Convert files with games to observation/labels')
    parser.add_argument('--trump', action='store_true', help='Generate files for trump decision')
    parser.add_argument('--shuffle', action='store_true', help='Shuffle entries')
    parser.add_argument('--output', type=str, help='Base name of the output files', default='')
    parser.add_argument('--output_dir', type=str, help='Directory for output files', default='.')
    parser.add_argument('--max_entry', type=int, default=100000, help='Maximal number of entries in one file')
    parser.add_argument('files', type=str, nargs='+', help='The log files')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.trump:
        generate_logs_trump(args.files, args.output, args.output_dir, args.max_entry, args.shuffle)
    else:
        generate_logs(args.files, args.output, args.output_dir, args.max_entry, args.shuffle)


if __name__ == '__main__':
    main()
