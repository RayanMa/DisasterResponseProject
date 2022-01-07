import json
import plotly
import pandas as pd
import pickle 

import plotly.graph_objs as go
import plotly.express as px
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
from plotly.graph_objs import Scatter
from plotly.graph_objs import Line

from sklearn.externals import joblib
from sqlalchemy import create_engine


app = Flask(__name__)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens

# load data
engine = create_engine('sqlite:///../data/DisasterResponse.db')
df = pd.read_sql_table('Tweets', engine)

# load model
model = joblib.load("../models/classifier.pkl")






# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    
    
    
    #Plot 2 code
    plot2_df=df.drop(['id','message','original','genre',],axis=1)
    def most_cat():
        for i in plot2_df:
            test_sample=plot2_df[plot2_df[i]==1].sum()
            print(test_sample)
            return test_sample
        pass
  
    category_ouc=most_cat()
    category_names=list(plot2_df.columns.values)
    
    #plot 3 code
    plot3=df[['death','food']]
             
    def relation():
        for i in plot3:
            test_sample=plot3[plot3[i]==1].sum()
            print(test_sample)
            return test_sample
        pass
        

    plot3_relation=relation()
    
    
    
    # create visuals
    # TODO: Below is an example - modify to create your own visuals
    graphs = [
        {
            'data': [
               Bar(
                    x=genre_names,
                    y=genre_counts,
                    
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
                 
            }
        },
        
        
        #plot 2
        
      {
            'data': [
               Line(
                    x=category_names,
                    y=category_ouc,
                  
                )
            ],

            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Categories"
                }
            }
        }
        ,
        
        {
         'data': [
               
                    
             
            Bar (
                    x=plot3.columns.values,
                    y=plot3_relation,
           
                )
             
            ],

            'layout': {
                'title': 'The relation btween Death and Food categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Categories"
                }
            }
        }
        
               
               
             
                    
    
        
    ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '') 

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file. 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)
    #print(plot2_df[plot2_df['offer']==1].sum())
    #print(df_plot3)


if __name__ == '__main__':
    main()