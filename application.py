from flask import Flask, request, render_template
import requests
import newspaper
import urllib
from newspaper import Article
import pickle
import nltk
nltk.download('punkt')
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'hoax'

mysql = MySQL(app)

with open('MODEL.pkl', 'rb') as myModel:
    model = pickle.load(myModel)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    url = request.get_data(as_text=True)[5:]
    url = urllib.parse.unquote(url)
    article = Article(str(url))
    article.download()
    article.parse()
    article.nlp()
    news = article.summary
    pred = model.predict([news])

    db = request.form
    link = db['news']
    hasil = pred[0]
    cur = mysql.connection.cursor()
    cur.execute("insert into data (URLs, Results) values(%s, %s)", (link, hasil))
    mysql.connection.commit()
    cur.close()

    return render_template('home.html', pred_text= 'The News is "{}"'.format(pred[0]))

@app.route('/About')
def about():
    return render_template('about.html')

@app.route('/Feedback')
def feed():
    return render_template('feed.html')

if __name__ == "__main__":
    app.run(debug=True, port=100)
