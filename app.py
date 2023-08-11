import os
from flask import Flask, Response, jsonify, request, render_template, redirect, session, abort
from database import db, Article, User
from protect_admin_page import is_authenticated
from gmail_send import send_email
from werkzeug.security import generate_password_hash


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///user.db'}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.permanent_session_lifetime      # устанавливает время жизни сессии 31 день

PASSWORD_TO_ADD_NEWS = os.getenv('PASSWORD_TO_ADD_NEWS')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['POST', 'GET'])
def feedBackForm(): 
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phoneNumber')
    introduction = request.form.get('introduction')
    text = request.form.get('text')
    
    message = f'{name}\n{email}\n{phone}\n{introduction}\n{text}'

    # send message to email
    if message != 'None\nNone\nNone\nNone\nNone':
        send_email(message=message)
        return redirect('/')
    else:
        print('Form is Empty!')
    
    return Response(status=200)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash = generate_password_hash(request.form['password'])

        user = User(username=username, password=hash)

        if is_authenticated(username, password):
            session['user_id'] = username
            return Response(status=200)

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return 'ERROR APPENDING USER TO DATABASE'


    return render_template('login.html')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'user_id' not in session:
        abort(404)
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD_TO_ADD_NEWS:  # Проверка пароля (замените на свой)
            title = request.form['title']
            text = request.form['text']
            image_url = request.form['image_url']

            article = Article(title=title, text=text, image_url=image_url)            
            try:
                db.session.add(article)
                db.session.commit()
            except:
                return 'ERROR'

    return render_template('add_news.html')


@app.route('/news_list', methods=['POST', 'GET'])
def news_list():
    articles = Article.query.order_by(Article.date.desc()).all()
    
    article_list = []
    for article in articles:
        article_dict = {
            'id': article.id,
            'title': article.title,
            'text': article.text,
            'image_url': article.image_url,
            'date': article.date.strftime('%Y-%m-%d %H:%M:%S')
        }
        article_list.append(article_dict)   

    return jsonify(article_list)


@app.route('/news_/<int:id>', methods=['POST', 'GET'])
def news_details(id):
    article = Article.query.get(id)

    article = Article.query.get(id)

    if article is None:
        return jsonify({'error': 'Article not found'})

    article_list = []
    article_dict = {
        'title': article.title,
        'text': article.text,
        'image_url': article.image_url,
        'date': article.date.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    article_list.append(article_dict)

    return jsonify(article_list)


@app.route('/news/<int:id>/delete', methods=['POST', 'GET'])
def news_delete(id):
    if 'user_id' not in session:
        abort(404)

    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return Response(status=200)
    except:
        return "ERROR DELETING"      


@app.errorhandler(404)
def page_not_found(error):
    print(f'{error}')
    return render_template('page_404.html', title='Not Found')


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=8000, debug=True)
