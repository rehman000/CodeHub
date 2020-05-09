from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from app import db
from app.models import User, Post
from app.posts.forms import PostForm
from flask import Flask
from flask_censor import Censor # This is based on profanity filter ... 
from profanity_check import predict


posts = Blueprint('posts', __name__)

# CRUD Methods: 

censor = Censor()
censor.set_censorchars('*')
# censor.import_wordlist("app/posts/wordlist")          # The default configuration is much MUCH better at detecting profanity the wordslist makes it inaccurate! 


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post(): 
    form = PostForm()                                                                               # Create instance of the  PostForm()

    if form.validate_on_submit():       # If user input is valid (i.e) no null characters, etc

        title_check = predict([form.title.data])
        content_check = predict([form.content.data])

        if (title_check[0] == 1 or content_check[0] == 1) and (current_user.profanity == False):
            title = censor.censor(form.title.data)          # Feature # 11: Profanity Filter ... 
            content = censor.censor(form.content.data)
            post = Post(title=title, content=content, author=current_user)          # Create instance of Post() and pass in user input given to the form
            current_user.reputation -= 1
            current_user.profanity = True
            db.session.commit()
            flash('Warning! Profanity detected! Since this is your first offense, Your reputation score has been reduced by 1. Any subsequent offense will reduce your reputation score by 5!', 'warning')
            return redirect(url_for('main.home'))                                                       # Redirect to Home page    

        if (title_check[0] == 1 or content_check[0] == 1) and (current_user.profanity == True):
            title = censor.censor(form.title.data)          # Feature # 11: Profanity Filter ... 
            content = censor.censor(form.content.data)
            post = Post(title=title, content=content, author=current_user)          # Create instance of Post() and pass in user input given to the form
            current_user.reputation -= 5
            db.session.commit()
            flash('Warning! Profanity detected! Your reputation score has been reduced by 5. You were warned!', 'danger') 
            return redirect(url_for('main.home'))                                                       # Redirect to Home page
        
        title = censor.censor(form.title.data)          # Feature # 11: Profanity Filter ... 
        content = censor.censor(form.content.data)
        post = Post(title=title, content=content, author=current_user)          # Create instance of Post() and pass in user input given to the form
        db.session.add(post)                                                                        # Mark this 'post' to be added to the database
        db.session.commit()                                                                         # Commit changes to db
        flash('Your post has been created!', 'success')                                             # Display success message! For anyone wondering 'success' is just a bootstrap class, it gives a green-ish hue.
        return redirect(url_for('main.home'))                                                       # Redirect to Home page
    
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')




@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)



@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()                                                       # Create an instance of the PostForm()
    
    if form.validate_on_submit():                                           # If the input is valid
        post.title = form.title.data                                        # The form title overwrites the post title
        post.content = form.content.data                                    # The form content overwrites the post content
        db.session.commit()                                                 # Commit changes to db! 
                                                                            # We do not need to add anything into the db, these objects are already in the db and being overwritten!
        flash('Your post has been successfully updated!', 'success')        # Display success message. For anyone wondering 'success' is a bootstrap class it gives a green-ish hue.
        return redirect(url_for('posts.post', post_id=post.id))             # Redirect to the post/id page
    if request.method == 'GET':
        form.title.data = post.title                                        # This ensures that the fields are populated with the previous text! But only if it's a 'GET' request.
        form.content.data = post.content                                    # This ensures that the fields are populated with the previous text! But only if it's a 'GET' request.
    
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')            # Redirect to Create_Post.html, but with some pre-filled text, and a newer legend! 




@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)                              
    db.session.delete(post)                                                 # Mark post for deletion in db
    db.session.commit()                                                     # Commit changes to db!
    flash('Your post has been successfully deleted!', 'success')            # Display success message. For anyone wondering 'success' is a bootstrap class it gives a green-ish hue.
    return redirect(url_for('main.home'))                                   # Redirect to the Home page

