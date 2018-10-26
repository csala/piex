# -*- coding: utf-8 -*-

import logging

import numpy as np
from mlblocks import MLPipeline
from sklearn.model_selection import KFold

from mit_d3m import load_dataset

LOGGER = logging.getLogger(__name__)


def get_split(X, y, indexes):
    if hasattr(X, 'iloc'):
        X = X.iloc[indexes]
    else:
        X = X[indexes]

    if y is not None:
        if hasattr(y, 'iloc'):
            y = y.iloc[indexes]
        else:
            y = y[indexes]

    return X, y


def pipeline_score(pipeline_dict, X, y, scorer, context=None, n_splits=5, cv=None):

    context = context or dict()

    LOGGER.debug('CV Scoring pipeline %s')

    cv_scores = list()
    cv = cv or KFold(n_splits=n_splits, shuffle=True)

    for fold, (train_index, test_index) in enumerate(cv.split(X, y)):
        LOGGER.debug('Scoring fold: %s', fold)

        X_train, y_train = get_split(X, y, train_index)
        pipeline = MLPipeline.from_dict(pipeline_dict)
        pipeline.fit(X_train, y_train, **context)

        X_test, y_test = get_split(X, y, test_index)
        pred = pipeline.predict(X_test, **context)

        score = scorer(pred, y_test)
        cv_scores.append(score)

        LOGGER.debug('Fold %s score: %s', fold, score)

    return np.mean(cv_scores)


def pipeline_dataset_score(pipeline_dict, dataset_name, n_splits=5, cv=None):
    dataset = load_dataset(dataset_name)

    X = dataset.X
    y = dataset.y
    scorer = dataset.scorer
    context = dataset.context

    return pipeline_score(pipeline_dict, X, y, scorer, context, n_splits, cv)


def score_pipeline(pipeline_dict, n_splits=5, cv=None):
    return pipeline_dataset_score(pipeline_dict, pipeline_dict['dataset'], n_splits, cv)