import sys
import nltk
from sklearn import metrics
nltk.download(['punkt', 'wordnet', 'averaged_perceptron_tagger','stopwords'])
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import make_multilabel_classification
from sklearn.metrics import confusion_matrix,accuracy_score, f1_score, classification_report
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pickle

#load function with global X and Y
def load_data(database_filepath):
    global X
    global Y
    con = sqlite3.connect(database_filepath)
    df = pd.read_sql_query("SELECT * from tweets", con)
    cur = con.cursor()
    X = df.message
    Y = df.drop(['id','message','original','genre'],axis=1)
    category_names=list(Y.columns.values)
    return X , Y , category_names
    pass

#Tokeniztion function
def tokenize(text):
    text = text.lower() 
    words = word_tokenize(text)
    words = [w for w in words if w not in stopwords.words("english")]
    lemmed = [WordNetLemmatizer().lemmatize(w) for w in words]
    return lemmed
    pass

#building
def build_model():
    #pipline
    forest=RandomForestClassifier()
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf',  MultiOutputClassifier(RandomForestClassifier()))
                        ])
    #grid search parameters
    parameters = {
          'clf__estimator__criterion':('gini', 'entropy'),
          'clf__estimator__max_depth': (None,2)
             }
    #grid search  
    cv = GridSearchCV(pipeline, param_grid=parameters)
    return cv
    pass


def evaluate_model(model, X_test, Y_test, category_names):
    # Printing Report with F1 score , recall and percision
    Y_pred=model.predict(X_test)
  
    for i, c in enumerate(Y) :
       print(metrics.classification_report(Y_test.iloc[:,i], Y_pred[:,i]))
    
    
    pass

#saving the model to pkl file
def save_model(model, model_filepath):
    filename = model_filepath
    pickle.dump(model, open(filename, 'wb'))
    pass


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        report = evaluate_model(model, X_test, Y_test, category_names)
        print(report)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()