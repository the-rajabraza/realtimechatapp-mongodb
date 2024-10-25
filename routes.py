from flask import render_template, request, redirect, session, url_for
import dbfunctions

def register_routes(app, db, session):
    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            dbfunctions.add_user(db, username)
            session['username'] = username
            session.permanent = True
            return redirect(url_for('users'))
        return render_template('login.html')

    @app.route('/users')
    def users():
        if 'username' not in session:
            return redirect(url_for('login'))

        current_username = session['username']
        all_users = dbfunctions.get_all_users(db, current_username)
        chatted_users = dbfunctions.get_chatted_users(db, current_username)
        chatted_usernames = {user['username'] for user in chatted_users}
        available_users = [user for user in all_users if user['username'] not in chatted_usernames]

        return render_template('users.html', username=current_username, available_users=available_users, chatted_users=chatted_users)

    @app.route('/chat/<string:partner>')
    def chat(partner):
        if 'username' not in session:
            return redirect(url_for('login'))

        current_username = session['username']
        messages = dbfunctions.get_messages(db, current_username, partner)

        return render_template('chat.html', username=current_username, partner=partner, messages=messages)

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'username' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            avatar = request.form['avatar']
            status_message = request.form['status_message']
            dbfunctions.update_user_profile(db, session['username'], avatar, status_message)
            return redirect(url_for('profile'))

        user_profile = dbfunctions.get_user_profile(db, session['username'])
        return render_template('profile.html', username=session['username'], profile=user_profile)

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))