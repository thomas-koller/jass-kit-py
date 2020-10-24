# HSLU
#
# Created by Thomas Koller on 24.10.2020
#

# split complete game files randomly into train, validation and test
# ids of players are not evaluated for the split

import argparse
import os
import json
import numpy as np

from jass.logs.game_log_entry import GameLogEntry
from jass.logs.log_entry_file_generator import LogEntryFileGenerator


def main():
    parser = argparse.ArgumentParser(description='Read log files and convert them to train, val and test files')
    parser.add_argument('--output', type=str, help='Base name of the output files', default='')
    parser.add_argument('--output_dir', type=str, help='Directory for output files')
    parser.add_argument('--train_split', type=float, default=0.6, help='Percentage of train data')
    parser.add_argument('--val_split', type=float, default=0.2, help='Percentage of validation data')
    parser.add_argument('--test_split', type=float, default=0.2, help='Percentage of test data')
    parser.add_argument('--seed', type=int, default=42, help='Seed for random number generator')
    parser.add_argument('--max_games', type=int, default=100000, help='Maximal number of games in one file')
    parser.add_argument('files', type=str, nargs='+', help='The log files')

    arg = parser.parse_args()

    if arg.output_dir is not None:
        if not os.path.exists(arg.output_dir):
            print('Creating directory {}'.format(arg.output_dir))
            os.makedirs(arg.output_dir)
        basename = os.path.join(arg.output_dir, arg.output)
    else:
        basename = arg.output

    prob = [arg.train_split, arg.val_split, arg.test_split]
    np.random.seed(arg.seed)

    with LogEntryFileGenerator(basename + 'train_', max_entries=arg.max_games, max_buffer=arg.max_games, shuffle=True) as train, \
         LogEntryFileGenerator(basename + 'val_', max_entries=arg.max_games, max_buffer=arg.max_games, shuffle=True) as val, \
         LogEntryFileGenerator(basename + 'test_', max_entries=arg.max_games, max_buffer=arg.max_games, shuffle=True) as test:

        nr_total = 0
        nr_train = 0
        nr_val = 0
        nr_test = 0

        for filename in arg.files:
            print('Processing file {}'.format(filename))
            with open(filename, mode='r') as file:
                for line in file:
                    entry = json.loads(line)
                    nr_total += 1
                    set_chosen = np.random.choice(3, p=prob)
                    if set_chosen == 0:
                        train.add_entry(entry)
                        nr_train += 1
                    elif set_chosen == 1:
                        val.add_entry(entry)
                        nr_val += 1
                    elif set_chosen == 2:
                        test.add_entry(entry)
                        nr_test += 1

                    _print_progress(nr_total)

    print('Train: {}\tVal: {}\tTest: {}\tTotal: {}'.format(nr_train, nr_val, nr_test, nr_total))

def _print_progress(nr):
    if nr % 1000 == 0:
        print('.', end='', flush=True)
    if nr % 50000 == 0:
        # new line
        print('')


if __name__ == '__main__':
    main()
