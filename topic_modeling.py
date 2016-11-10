import os
import sys
import numpy as np
import pandas as pd
import spacy
import matplotlib.pyplot as plt
from PIL import Image
from clean_text import STOPLIST
from wordcloud import WordCloud
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
plt.style.use('ggplot')


class NMFCluster(object):
    '''
    Class to run NMF clustering on a corpus of text
    '''

    def __init__(self, pro_or_con, num_topics, tfidf_max_features=10000, tfidf_max_df=0.95, tfidf_min_df=1000, nmf_alpha=.1, nmf_l1_ratio=0.25, random_state=None):
        self.pro_or_con = pro_or_con
        self.num_topics = int(num_topics)
        self.tfidf_max_features = tfidf_max_features
        self.tfidf_max_df = tfidf_max_df
        self.tfidf_min_df = tfidf_min_df
        self.nmf_alpha = nmf_alpha
        self.nmf_l1_ratio = nmf_l1_ratio
        self.random_state = random_state
        self.stop_words = STOPLIST

    def fit_nmf(self, df):
        '''
        Function to run NMF clustering on dataframe

        INPUT:
            df: pandas Dataframe containing 'lemmatized_text' column for NMF
        '''
        self.fit_tfidf(df)
        self.nmf = NMF(n_components=self.num_topics, alpha=self.nmf_alpha,
                       l1_ratio=self.nmf_l1_ratio, random_state=self.random_state).fit(self.tfidf_matrix)
        self.W_matrix = self.nmf.transform(self.tfidf_matrix)
        sums = self.W_matrix.sum(axis=1)
        self.W_pct = self.W_matrix / sums[:, None]
        self.labels = self.W_pct >= 0.20

    def fit_tfidf(self, df):
        '''
        Function to fit a TF-IDF matrix to a corpus of text

        INPUT:
            df: df with 'lemmatized_text' to analyze
        '''
        self.tfidf = TfidfVectorizer(input='content', use_idf=True, lowercase=True,
                                     max_features=self.tfidf_max_features, max_df=self.tfidf_max_features, min_df=self.tfidf_min_df)
        self.tfidf_matrix = self.tfidf.fit_transform(
            df['lemmatized_text']).toarray()
        self.tfidf_features = np.array(self.tfidf.get_feature_names())
        self.tfidf_reverse_lookup = {
            word: idx for idx, word in enumerate(self.tfidf_features)}

    def top_words_by_topic(self, n_top_words, topic=None):
        '''
        Function to find the top n words in a topic

        INPUT:
            n_top_words: number of words to print in the topic summary
            topic: index of topic
        '''
        if topic != None:
            idx = np.argsort(self.nmf.components_[topic])[-n_top_words:][::-1]
            return self.tfidf_features[idx]
        else:
            idxs = [np.argsort(topic)[-n_top_words:][::-1]
                    for topic in self.nmf.components_]
            return np.array([self.tfidf_features[idx] for idx in idxs])

    def topic_attribution_by_document(self, document_idx):
        '''
        Function to calculate percent attributability for each topic and doc

        INPUT:
            document_idx: index of document in corpus
        '''
        idxs = np.where(self.labels[document_idx] == 1)[0]
        idxs = idxs[np.argsort(self.W_pct[document_idx, idxs])[::-1]]
        return np.array([(idx, pct) for idx, pct in zip(idxs, self.W_pct[document_idx, idxs])])

    def print_topic_summary(self, df, topic_num, num_words=20):
        '''
        Function to print summary of a topic from NMF clustering

        INPUT:
            df: pandas DataFrame that NMF clustering was run on
            topic_num: index of topic from clustering
            num_words: top n words to print in summary
        '''
        num_reviews = self.labels[:, topic_num].sum()
        print 'Summary of Topic {}:'.format(topic_num)
        print 'Number of reviews in topic: {}'.format(num_reviews)
        print 'Top {} words in topic:'.format(num_words)
        print self.top_words_by_topic(num_words, topic_num)
        if not num_reviews:
            return None

    def topic_word_frequency(self, topic_idx):
        ''' Return (word, frequency) tuples for creating word cloud
        INPUT:
            topic_idx: int
        '''
        freq_sum = np.sum(self.nmf.components_[topic_idx])
        frequencies = [
            val / freq_sum for val in self.nmf.components_[topic_idx]]
        return zip(self.tfidf_features, frequencies)

    def plot_topic(self, topic_idx):
        '''
        Function to plot a wordcloud based on a topic

        INPUT:
            topic_idx: index of topic from NMF clustering
        '''
        title = raw_input('Enter a title for this plot: ')
        num_reviews = self.labels[:, topic_idx].sum()
        word_freq = self.topic_word_frequency(topic_idx)
        wc = WordCloud(width=2000, height=1000, max_words=150,
                       background_color='white')
        wc.fit_words(word_freq)
        fig = plt.figure(figsize=(16, 8))
        ax = fig.add_subplot(111)
        ax.set_title('Topic {}: {}\nNumber of Reviews in Topic: {}'.format(
            topic_idx, title, num_reviews), fontsize=24)
        ax.axis('off')
        ax.imshow(wc)
        name = 'topic_' + str(topic_idx) + '.png'
        if self.pro_or_con == 'pro':
            img_path = os.path.join('images', 'positive')
        else:
            img_path = os.path.join('images', 'negative')
        plt.savefig(os.path.join(img_path, name))
        plt.show()

    def visualize_topics(self, df):
        '''
        Function to cycle through all topics and print summary and plot cloud

        INPUT:
            df: pandas DataFrame (source for NMF text)
        '''
        for i in range(self.num_topics):
            self.print_topic_summary(df, i)
            self.plot_topic(i)
            print ''


if __name__ == '__main__':
    pros_df = pd.read_pickle(os.path.join('data', 'pros_df.pkl'))
    cons_df = pd.read_pickle(os.path.join('data', 'cons_df.pkl'))

    nmf_pros = NMFCluster('pro', 21, random_state=42)
    nmf_cons = NMFCluster('con', 10, random_state=42)
    nmf_pros.fit_nmf(pros_df)
    nmf_cons.fit_nmf(cons_df)

    nmf_pros.visualize_topics(pros_df)
    nmf_cons.visualize_topics(cons_df)
