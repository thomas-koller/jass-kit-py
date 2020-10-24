# HSLU
#
# Created by Thomas Koller on 05.08.20
#
"""
Convert Swisslos log files to match log files.
"""


import argparse
from datetime import datetime
import glob
import json
import os
import logging
from json import JSONDecodeError
from typing import List

from jass.game.game_state import GameState
from jass.logs.log_entry_file_generator import LogEntryFileGenerator
from jass.logs.game_log_entry import GameLogEntry


class LogParserSwisslos:
    """
    Class to parse the log files from swisslos, the file format is similar to the match log, but contains
    not only json in a line and multiple games in a line (all between the same players). The actual match
    information is still read by GameState.from_json().
    """

    @staticmethod
    def parse_rounds(filename) -> List[GameLogEntry]:
        """
        Parse games including information about the players and the date which is stored in a list of objects.

        The log file is in the format specified and supplied by Swisslos, which includes multiple games with
        the same information about the date and players.
        Args:
            filename: file to read logs from
        Returns:
            A list of objects of type GameLogEntry
        """
        games = []
        with open(filename, 'r') as file:
            nr_lines = 0
            nr_rounds = 0
            nr_skipped_lines = 0
            nr_skipped_rounds = 0
            # one line contains one log record (with multiple rounds)
            for line in file:
                nr_lines += 1
                # start of line contains:
                # 27.11.17 20:10:08,140 | INFO |  |  |  |  |
                # so we read until the first {
                index = line.find('{')
                # if we find an index, we attempt to read the date
                if index > 17:
                    datetime_string = line[0:17]
                    date = datetime.strptime(datetime_string, '%d.%m.%y %H:%M:%S')
                else:
                    date = None

                if index != -1:
                    try:
                        line_json = json.loads(line[index:])
                    except JSONDecodeError as e:
                        logging.getLogger(__name__).error('Error decoding json: at line {}, {}, '
                                                          'skipping line'.format(nr_lines, e))
                        nr_skipped_lines += 1
                        continue
                    # read the players for those rounds
                    if 'players' in line_json:
                        players = line_json['players']
                    else:
                        # default player (not registered)
                        players = [0, 0, 0, 0]
                    for r in line_json['rounds']:
                        if r is not None:
                            game_read = GameState.from_json(r)
                            if game_read is not None:
                                if game_read.nr_played_cards != 36:
                                    nr_skipped_rounds += 1
                                else:
                                    nr_rounds += 1
                                    games.append(GameLogEntry(game=game_read, date=date, player_ids=players))
                            else:
                                nr_skipped_rounds += 1

        logging.getLogger(__name__).info('Read {} valid rounds from file'.format(nr_rounds))
        logging.getLogger(__name__).info('Skipped {} lines'.format(nr_skipped_lines))
        logging.getLogger(__name__).info('Skipped {} rounds'.format(nr_skipped_rounds))
        return games


def main():
    parser = argparse.ArgumentParser(description='Read log files and convert them to match log files')
    parser.add_argument('--output', type=str, help='Base name of the output files', default='game_')
    parser.add_argument('--output_dir', type=str, help='Directory for output files')
    parser.add_argument('--max_games', type=int, default=100000, help='Maximal number of games in one file')
    parser.add_argument('--max_buffer', type=int, default=100000, help='Size of buffer to shuffle')
    parser.add_argument('--recursive', action='store_true', help='True if file argument is a directory '
                                                                 'that should be searched recursively for '
                                                                 'files with the extension .txt.')
    parser.add_argument('files', type=str, nargs='+', help='The log files or a directory')
    arg = parser.parse_args()

    if arg.recursive:
        if len(arg.files) > 1:
            print('Please give only one directory name when using --recursive')
            parser.print_usage()
            return
        print('Searching directory...')
        search_path = os.path.join(arg.files[0], '**/*.txt')
        files = glob.glob(search_path, recursive=True)
        files.sort()
        print('Found {} files.'.format(len(files)))
    else:
        files = arg.files

    if arg.output_dir is not None:
        directory = arg.output_dir
    else:
        directory = ''

    basename = os.path.join(arg.output_dir, arg.output)

    logging.basicConfig(level=logging.INFO)
    nr_total = 0

    os.makedirs(arg.output_dir, exist_ok=True)

    with LogEntryFileGenerator(basename, arg.max_games, arg.max_buffer) as log:
        for f in files:
            print('Processing file {}'.format(f))
            log_entries = LogParserSwisslos.parse_rounds(f)
            nr_total += len(log_entries)

            for entry in log_entries:
                log.add_entry(entry.to_json())
                _print_progress(nr_total)

    print('Total: {}'.format(nr_total))


def _print_progress(nr_rounds):
    if nr_rounds % 1000 == 0:
        print('.', end='', flush=True)
    if nr_rounds % 100000 == 0:
        # new line
        print('')


if __name__ == '__main__':
    main()
