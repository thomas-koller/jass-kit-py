"""
Train and compare trump selection models on the Swisslos data (exercise 8), and export the linear model
as numpy weights for the bot.

    python -m jass.train.trump.train --csv path/to/2018_10_18_trump.csv --out models/trump_linear.npz

Needs the training extra: pip install -e .[train]
"""
import argparse
import logging
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score, train_test_split

from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.agents.trump.features import FOREHAND_INDEX, NR_CLASSES, PUSH_CLASS, label_to_class
from jass.game.game_observation import GameObservation
from jass.train.trump.data import load_trump_csv

CLASS_NAMES = ['D', 'H', 'S', 'C', 'OBE', 'UNE', 'PUSH']

MODELS = {
    'logreg': lambda seed: LogisticRegression(max_iter=1000),
    'forest': lambda seed: RandomForestClassifier(n_estimators=200, min_samples_leaf=5, n_jobs=-1, random_state=seed),
    'boosting': lambda seed: HistGradientBoostingClassifier(max_iter=300, random_state=seed),
}


def mask_push(proba: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Predict the best class, never push when the features say push is not allowed (same rule as the bot)."""
    proba = proba.copy()
    proba[X[:, FOREHAND_INDEX] == 0, PUSH_CLASS] = -np.inf
    return np.argmax(proba, axis=1)


def full_proba(model, X: np.ndarray) -> np.ndarray:
    """predict_proba with one column per class 0..6, even if a class was missing in training."""
    proba = np.zeros((len(X), NR_CLASSES))
    proba[:, model.classes_] = model.predict_proba(X)
    return proba


def rule_based_predictions(X: np.ndarray) -> np.ndarray:
    """Baseline: what the hand written rule based trump selection picks for each hand."""
    agent = AgentRuleBasedSchieber()
    obs = GameObservation()
    predictions = np.empty(len(X), dtype=np.int64)
    for i, row in enumerate(X):
        obs.hand = row[:36].astype(np.int32)
        obs.forehand = -1 if row[FOREHAND_INDEX] == 1 else 0
        predictions[i] = label_to_class(agent.action_trump(obs))
    return predictions


def report(name: str, y_true: np.ndarray, y_pred: np.ndarray, seconds: float) -> dict:
    result = dict(name=name,
                  accuracy=accuracy_score(y_true, y_pred),
                  macro_f1=f1_score(y_true, y_pred, average='macro'),
                  seconds=seconds)
    print('{name:<10} accuracy {accuracy:.4f}  macro-F1 {macro_f1:.4f}  ({seconds:.1f}s)'.format(**result))
    return result


def print_confusion(y_true: np.ndarray, y_pred: np.ndarray):
    matrix = confusion_matrix(y_true, y_pred, labels=range(NR_CLASSES))
    print('rows: true, columns: predicted')
    print('      ' + ''.join('{:>7}'.format(n) for n in CLASS_NAMES))
    for name, line in zip(CLASS_NAMES, matrix):
        print('{:>6}'.format(name) + ''.join('{:>7}'.format(v) for v in line))


def save_linear_model(path: Path, model: LogisticRegression):
    """Write the weights in the format jass.agents.trump.trump_model reads: logits = features @ weights.T + bias."""
    weights = np.zeros((NR_CLASSES, model.coef_.shape[1]), dtype=np.float32)
    bias = np.full(NR_CLASSES, -np.inf, dtype=np.float32)
    weights[model.classes_] = model.coef_
    bias[model.classes_] = model.intercept_
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, weights=weights, bias=bias, format_version=np.array(1))
    print('Saved linear model to {}'.format(path))


def main():
    parser = argparse.ArgumentParser(description='Train trump selection models on the Swisslos data')
    parser.add_argument('--csv', required=True, type=Path, help='2018_10_18_trump.csv')
    parser.add_argument('--out', type=Path, default=Path('models/trump_linear.npz'), help='exported linear model')
    parser.add_argument('--models', nargs='+', default=list(MODELS), choices=list(MODELS))
    parser.add_argument('--nrows', type=int, default=None, help='only read the first rows, for quick runs')
    parser.add_argument('--cv', type=int, default=0, help='k-fold cross validation on the training set, 0 = off')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    data = load_trump_csv(args.csv, nrows=args.nrows)
    X_train, X_test, y_train, y_test = train_test_split(data.X, data.y, test_size=0.2, stratify=data.y,
                                                        random_state=args.seed)
    print('train {}, test {}, class share in test: {}'.format(
        len(y_train), len(y_test), np.round(np.bincount(y_test, minlength=NR_CLASSES) / len(y_test), 3)))

    start = time.time()
    report('rule', y_test, rule_based_predictions(X_test), time.time() - start)

    fitted = {}
    for name in args.models:
        model = MODELS[name](args.seed)
        if args.cv:
            scores = cross_val_score(model, X_train, y_train, cv=args.cv, n_jobs=-1)
            print('{:<10} {}-fold CV accuracy {:.4f} +- {:.4f}'.format(name, args.cv, scores.mean(), scores.std()))
        start = time.time()
        model.fit(X_train, y_train)
        report(name, y_test, mask_push(full_proba(model, X_test), X_test), time.time() - start)
        fitted[name] = model

    if 'logreg' in fitted:
        print_confusion(y_test, mask_push(full_proba(fitted['logreg'], X_test), X_test))
        save_linear_model(args.out, fitted['logreg'])


if __name__ == '__main__':
    main()
