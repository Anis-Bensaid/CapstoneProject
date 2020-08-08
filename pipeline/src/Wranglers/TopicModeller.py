import os

import gensim
import pandas as pd

PATH_TO_MODELS = '../models'


class TopicModeller:
    def __init__(self, path_to_models=PATH_TO_MODELS):
        self.path_to_models = path_to_models
        self.topics_grid = {'makeup_face': {'columns': ['topic_1', 'topic_2', 'topic_3', 'topic_4']},
                            'makeup_lips': {'columns': ['topic_1', 'topic_2', 'topic_4', 'topic_3']},
                            'makeup_eyes': {'columns': ['topic_1', 'topic_2', 'topic_4', 'topic_3']},
                            'makeup_face_color': {'columns': ['topic_1', 'topic_2', 'topic_3', 'topic_4']},
                            'makeup_other': {'columns': ['topic_1', 'topic_3', 'topic_4', 'topic_2']},
                            'skincare_all': {'columns': ['topic_1', 'topic_3', 'topic_2', 'topic_4']}}
        self.get_models()

    def get_models(self):
        for category in self.topics_grid.keys():
            for filename in os.listdir(PATH_TO_MODELS):
                if filename.find(category) != -1 and filename.find('.npy') != -1:
                    self.topics_grid[category]['model'] = gensim.models.LdaModel.load(
                        os.path.join(PATH_TO_MODELS, filename.split('.')[0]))

    def add_topics(self, reviews):
        for col in ['topic_1', 'topic_2', 'topic_3', 'topic_4']:
            reviews[col] = 0

        self.topics_grid['makeup_face']['tokens'] = reviews[
            (reviews['major_category'] == 'Makeup') & (reviews['application'] == 'Face')]['tokens']
        self.topics_grid['makeup_lips']['tokens'] = reviews[
            (reviews['major_category'] == 'Makeup') & (reviews['application'] == 'Lips')]['tokens']
        self.topics_grid['makeup_eyes']['tokens'] = reviews[
            (reviews['major_category'] == 'Makeup') & (reviews['application'] == 'Eyes')]['tokens']
        self.topics_grid['makeup_face_color']['tokens'] = reviews[
            (reviews['major_category'] == 'Makeup') & (reviews['application'] == 'Face Color')]['tokens']
        self.topics_grid['makeup_other']['tokens'] = reviews[(reviews['major_category'] == 'Makeup') & (
            ~reviews['application'].isin(['Face', 'Lips', 'Eyes', 'Face Color']))]['tokens']
        self.topics_grid['skincare_all']['tokens'] = reviews[reviews['major_category'] == 'Skincare']['tokens']

        for category in self.topics_grid.keys():
            lda = self.topics_grid[category]['model']
            topics = pd.DataFrame(gensim.matutils.corpus2csc(
                lda.get_document_topics(
                    [lda.id2word.doc2bow(text) for text in self.topics_grid[category]['tokens'].tolist()
                     ])).T.toarray(),
                                  columns=self.topics_grid[category]['columns'])
            reviews.loc[
                self.topics_grid[category]['tokens'].index, ['topic_1', 'topic_2', 'topic_3', 'topic_4']] = topics
        return reviews
