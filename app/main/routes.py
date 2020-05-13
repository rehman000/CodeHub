from flask import render_template, request, Blueprint, flash
from flask_login import current_user 
from app.models import User, Post
from app.users.utils import blacklist 

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():                                                                                                         # Testing Complete. I no longer need to use dummy data! Horray!!! :D 
    page = request.args.get('page', 1, type=int)                                                                    # We request a page, the default page is 1, of type int
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)                            # Instead of using query.all(), I've changed this to query.paginate() ... 
                                                                                                                    # By using .query.order_by(Post.date_posted.desc())  I am able to show posts in a descending order of creation.
                                                                                                                    # Translation: The newer posts will be seen on the top, while the older posts will sink to the bottom and eventually to other paginated pages! 
    # is_shown = False
    if (current_user.is_authenticated and current_user.blacklisted == False and current_user.reputation < 0):        # Feature # 6: From the Spec Sheet! 
        flash('Your reputation became negative! You are being black listed!', 'danger')
        blacklist(current_user)

    return render_template('home.html', posts=posts) 


@main.route('/about')
def about():
    return render_template('about.html', title='About us')
