"""Blogly application."""

from flask import Flask, render_template, redirect, request
from models import db, connect_db, USER, Post, Tag
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly-part-three'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'helloimasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()



# ***** HOME PAGE AND USERS ROUTES *****


@app.route('/')
def home_page():
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('home-page.html', posts=posts)

@app.route('/users')
def user_page():
    users = USER.query.order_by(USER.last_name, USER.first_name).all()
    return render_template('user-page.html', users=users)

@app.route('/users/new', methods=["GET"])
def show_add_user_form():
    return render_template('add-user.html')

@app.route('/users/new', methods=["POST"])
def add_user():
    first_name = request.form['first-name']
    last_name = request.form['last-name']
    img_url = request.form['img-url'] or None
    
    new_user = USER(first_name=first_name, last_name=last_name, img_url=img_url)

    db.session.add(new_user)
    db.session.commit()
    return redirect('/users')

@app.route("/users/<int:id>")
def user_details(id):
    user = USER.query.get_or_404(id)
    return render_template('details.html', user=user)

@app.route('/users/<int:id>/edit', methods=["GET"])
def edit_user(id):
    user = USER.query.get_or_404(id)
    return render_template('edit-user.html', user=user)

@app.route('/users/<int:id>/edit', methods=["POST"])
def save_updated_user(id):
        user = USER.query.get_or_404(id)
        user.first_name = request.form['first-name']
        user.last_name = request.form['last-name']
        user.img_url = request.form['img-url']
        db.session.add(user)
        db.session.commit()
        return redirect('/users')

@app.route('/users/<int:id>/delete')
def delete_user(id):
    user = USER.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')



# ***** POSTS ROUTES *****


@app.route('/users/<int:id>/posts/new', methods=['GET'])
def show_post_form(id):
    user = USER.query.get_or_404(id)
    tags = Tag.query.all()
    return render_template('add-post-form.html', user=user, tags=tags)

@app.route('/users/<int:id>/posts/new', methods=['POST'])
def add_post(id):
    user = USER.query.get_or_404(id)
    title = request.form['title']
    content = request.form['post-content']

    tags_ids = request.form.getlist('tags')
    tags = Tag.query.filter(Tag.id.in_(tags_ids)).all()

    new_post = Post(title=title, 
                    content=content, 
                    user=user,
                    tags=tags)

    db.session.add(new_post)
    db.session.commit()
    
    return redirect(f'/users/{id}')

@app.route('/posts/<int:id>')
def show_post_details(id):
    post = Post.query.get_or_404(id)
    return render_template('post-details.html', post=post)

@app.route('/posts/<int:id>/edit', methods=['GET'])
def show_post_edit(id):
    post = Post.query.get_or_404(id)
    tags = Tag.query.all()
    return render_template('post-edit-form.html', post=post, tags=tags)

@app.route('/posts/<int:id>/edit', methods=['POST'])
def handle_post_edit(id):
    post = Post.query.get_or_404(id)
    post.title = request.form['edited-title']
    post.content = request.form['edited-post-content']

    tags_ids = request.form.getlist('tags')
    post.tags = Tag.query.filter(Tag.id.in_(tags_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{post.user.id}')

@app.route('/posts/<int:id>/delete')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(f'/users/{post.user_id}')



# ***** TAGS ROUTES *****


@app.route('/tags')
def show_list_tags():
    tags = Tag.query.all()
    return render_template('list-tags.html', tags=tags)

@app.route('/tags/new', methods=['GET'])
def show_add_tags_form():
    return render_template('add-tags-form.html')

@app.route('/tags/new', methods=['POST'])
def handle_add_tags_form():
    tag = Tag(name=request.form['name'])
    db.session.add(tag)
    db.session.commit()
    return redirect('/tags')

@app.route('/tags/<int:id>')
def tag_details(id):
    tag = Tag.query.get_or_404(id)
    return render_template('tag-details.html', tag=tag)

@app.route('/tags/<int:id>/edit', methods=['GET'])
def edit_tag_form(id):
    tag = Tag.query.get_or_404(id)
    return render_template('tag-edit.html', tag=tag)

@app.route('/tags/<int:id>/edit', methods=['POST'])
def handle_edit_tag_form(id):
    edited_tag = Tag.query.get_or_404(id)
    edited_tag.name = request.form['name']

    db.session.add(edited_tag)
    db.session.commit()
    
    return redirect(f'/tags/{id}')

@app.route('/tags/<int:id>/delete')
def delete_tag(id):
    tag = Tag.query.get_or_404(id)

    db.session.delete(tag)
    db.session.commit()
    
    return redirect(f'/tags')