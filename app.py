from flask import Flask, render_template, request
import pandas as pd
import ast
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from flask_paginate import Pagination


app = Flask(__name__)

# Load the novel data and recommendations model
novel_data = pd.read_csv('data/wnM.csv')  


recommendations_data = pd.read_csv('data/recommendations.csv')

recommendations = {}
for index, row in recommendations_data.iterrows():
    novel_id = int(row['novel_id'])
    recs = ast.literal_eval(row['recommendations'])

novel_data['recommendations_y'] = novel_data['recommendations_y'].apply(lambda x: [item.strip() for item in x.split(',')])
 
@app.route('/')
def home():
    # Get sorting parameter
    sort_by = request.args.get('sort_by', 'rank')  
    search_query = request.args.get('search_query', '')

    # Filter novels based on search query using fuzzy matching
    if search_query:
        novel_titles = novel_data['title'].values
        fuzzy_matches = process.extract(search_query, novel_titles, limit=10, scorer=fuzz.token_sort_ratio)
        fuzzy_matches = [m for m, score in fuzzy_matches if score >= 70]
        filtered_novels = novel_data[novel_data['title'].isin(fuzzy_matches)]
    else:
        filtered_novels = novel_data
    
    # Sort filtered novels
    if sort_by == 'rank':
        sorted_novels = filtered_novels.sort_values(by='all_time_rank')
    else:
        sorted_novels = filtered_novels.sort_values(by='title')
    
    # Create a list of novels dynamically from the sorted DataFrame
    novels = sorted_novels.to_dict(orient='records')

    # Assuming you have a 'title' column in your DataFrame
    per_page = 15
    page = int(request.args.get('page', 1))
    total_pages = len(novels) // per_page + 1

    start = (page - 1) * per_page
    end = start + per_page
    novels_on_page = novels[start:end]

    return render_template('home.html', novels=novels_on_page, search_query=search_query, page=page, total_pages=total_pages)


@app.route('/novel/<int:novel_id>')
def novel(novel_id):
    try:
        novel_id = int(novel_id)
    except ValueError:
        return render_template('not_found.html')

    novel_details = novel_data[novel_data['novel_id'] == novel_id].to_dict('records')

    if not novel_details:
        return render_template('not_found.html')

    novel_recommendations = recommendations_data[recommendations_data['novel_id'] == novel_id]['recommendations'].tolist()
    
    # Retrieve chapters for the specific novel   novel_chapters = novel_data[novel_data['novel_id'] == novel_id]['chapters'].tolist()
    return render_template('novel.html',
                           novel_id=novel_id,
                           title=novel_details[0]['title'],
                           img_url=novel_details[0]['img_url'],
                           genres=novel_details[0]['genres'],
                           authors=novel_details[0]['authors'],
                           description=novel_details[0]['description'],
                           tags=novel_details[0]['tags'],
                           recommendations_y=novel_details[0]['recommendations_y'],
                           showtype=novel_details[0]['showtype'],
                           recommendations=novel_recommendations,
                           rating=novel_details[0]['rating'],
                           all_time_rank=novel_details[0]['all_time_rank'],
                           chapters=novel_details[0]['chapters'],  # Pass chapters to the template
                           year=novel_details[0]['year'],
                           status_coo=novel_details[0]['status_coo'])

if __name__ == '__main__':
    app.run(debug=True)