import os
from flask import Flask, request, render_template, redirect, session, abort
from database import db, Article, User
from protect_admin_page import is_authenticated
from gmail_send import send_email
from werkzeug.security import generate_password_hash
from forms import LoginForm, FeedBackForm, AddNewsForm


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
def data(): 
    form = FeedBackForm()
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
    
    return render_template('form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash = generate_password_hash(request.form['password'])

        user = User(username=username, password=hash)

        if is_authenticated(username, password):
            session['user_id'] = username
            return redirect('/admin_index')

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'ERROR APPENDING USER TO DATABASE'

    form = LoginForm()
    return render_template('login.html', form=form)


@app.route('/admin_index')
def admin_ndex():
    if 'user_id' not in session:
        abort(404)

    return render_template('admin_index.html')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'user_id' not in session:
        abort(404)
    form = AddNewsForm()
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
                return redirect('/admin_news_list')
            except:
                return 'ERROR'

    return render_template('add_news.html', form=form)


@app.route('/news_list', methods=['POST', 'GET'])
def news_list():
    articles = Article.query.order_by(Article.date.desc()).all()

    return render_template('news_list.html', articles=articles)


@app.route('/admin_news_list', methods=['POST', 'GET'])
def admin_news_list():
    if 'user_id' not in session:
        abort(404)

    articles = Article.query.order_by(Article.date.desc()).all()

    return render_template('admin_news_list.html', articles=articles)



@app.route('/news_/<int:id>', methods=['POST', 'GET'])
def news_details(id):
    article = Article.query.get(id)

    return render_template('news_details.html', article=article)


@app.route('/admin_news_/<int:id>', methods=['POST', 'GET'])
def admin_news_details(id):
    if 'user_id' not in session:
        abort(404)

    article = Article.query.get(id)

    return render_template('admin_news_details.html', article=article)


@app.route('/news/<int:id>/delete', methods=['POST', 'GET'])
def news_delete(id):
    if 'user_id' not in session:
        abort(404)

    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/news_list')  # Redirect to the list of news articles after successful deletion
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
