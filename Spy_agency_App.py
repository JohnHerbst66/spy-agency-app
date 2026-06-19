import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db_connection, create_users_table

# 1. COMMENT: Initialize the core Flask application and configure the session secret signature key.
app = Flask(__name__)
app.secret_key = 'spy_agency_ultra_secret_key'

def validate_agent_form(codename, username, pass_key, password):
    if not codename or not username or not pass_key or not password:
        return "❌ Access Denied: All classified fields are required."
    if len(codename) < 3 or len(codename) > 100:
        return "❌ Access Denied: Code name must be between 3 and 100 characters."
    if len(username) < 3 or len(username) > 100:
        return "❌ Access Denied: Username must be between 3 and 100 characters."
    if len(pass_key) < 6 or len(pass_key) > 100:
        return "❌ Access Denied: Pass key must be between 6 and 100 characters."
    if len(password) < 8 or len(password) > 100:
        return "❌ Access Denied: Password must be between 8 and 100 characters."
    return None

# ==========================================
# AUTHENTICATION PORTALS
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def login():
    # 2. COMMENT: Session protection checkpoint - if an agent already holds a valid security badge, bypass login form.
    if 'agent_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        connection = get_db_connection()
        agent = connection.execute(
            "SELECT * FROM agents WHERE username = ? AND password = ?", 
            (username, password)
        ).fetchone()
        connection.close()
        
        if agent:
            # 3. COMMENT: Issue a secure digital cookie badge to track individual agent identity across protected routes.
            session['agent_id'] = agent['id']
            session['codename'] = agent['codename']
            session['username'] = agent['username']
            flash(f"🔓 Access Granted. Welcome back, {agent['codename']}.", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Authentication Failed: Invalid Username or Password.", 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    # 4. COMMENT: Wipe and shred the user's current session badge memory completely to force safe system ejection.
    session.clear()
    flash("🔒 Logged out successfully. Mission accomplished.", 'success')
    return redirect(url_for('login'))

# ==========================================
# SECURE DASHBOARD & AGENT PAGES
# ==========================================

@app.route('/dashboard')
def dashboard():
    if 'agent_id' not in session:
        flash("🚫 Unauthorized Access: Please log in to view classified data.", 'error')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        codename = request.form.get('codename').strip()
        username = request.form.get('username').strip()
        pass_key = request.form.get('pass_key').strip()
        password = request.form.get('password').strip()
        
        error = validate_agent_form(codename, username, pass_key, password)
        if error:
            flash(error, 'error')
            return render_template('register.html', codename=codename, username=username, pass_key=pass_key, password=password)
        
        connection = get_db_connection()
        try:
            connection.execute(
                "INSERT INTO agents (codename, username, pass_key, password) VALUES (?, ?, ?, ?)",
                (codename, username, pass_key, password)
            )
            connection.commit()
            flash("⚡ Operative created successfully. Proceed to authentication terminal.", 'success')
            return redirect(url_for('login'))
        except Exception:
            flash("⚠️ Warning: Username already taken by another operative.", 'error')
        finally:
            connection.close()
            
    return render_template('register.html')

@app.route('/users')
def users():
    if 'agent_id' not in session:
        flash("🚫 Unauthorized Access: Log in required.", 'error')
        return redirect(url_for('login'))
        
    connection = get_db_connection()
    # 5. COMMENT: Query the entire user archive table and order the output dataset dynamically starting with newest records first.
    agents_list = connection.execute('SELECT * FROM agents ORDER BY id DESC').fetchall()
    connection.close()
    return render_template('users.html', agents=agents_list)

@app.route('/my_profile')
def my_profile():
    if 'agent_id' not in session:
        flash("🚫 Unauthorized Access: Log in required.", 'error')
        return redirect(url_for('login'))
        
    connection = get_db_connection()
    agent = connection.execute('SELECT * FROM agents WHERE id = ?', (session['agent_id'],)).fetchone()
    connection.close()
    return render_template('profile.html', agent=agent)

@app.route('/profile/<int:agent_id>')
def profile(agent_id):
    if 'agent_id' not in session:
        flash("🚫 Unauthorized Access: Log in required.", 'error')
        return redirect(url_for('login'))
        
    connection = get_db_connection()
    agent = connection.execute('SELECT * FROM agents WHERE id = ?', (agent_id,)).fetchone()
    connection.close()
    
    if agent is None:
        flash("❌ Warning: Target Agent not found in HQ database.", 'error')
        return redirect(url_for('users'))
        
    return render_template('profile.html', agent=agent)

# ==========================================
# PRELOADED UPDATE ROUTE
# ==========================================

@app.route('/update/<int:agent_id>', methods=['GET', 'POST'])
def update_profile(agent_id):
    if 'agent_id' not in session:
        flash("🚫 Unauthorized Access: Please log in first.", 'error')
        return redirect(url_for('login'))
        
    connection = get_db_connection()
    # 6. COMMENT: Preload operation - fetch the exact individual record matching the item identifier before drawing the template fields.
    agent = connection.execute('SELECT * FROM agents WHERE id = ?', (agent_id,)).fetchone()
    
    if agent is None:
        connection.close()
        flash("❌ Target Agent record not found.", 'error')
        return redirect(url_for('users'))

    if request.method == 'POST':
        codename = request.form.get('codename').strip()
        username = request.form.get('username').strip()
        pass_key = request.form.get('pass_key').strip()
        password = request.form.get('password').strip()
        
        error = validate_agent_form(codename, username, pass_key, password)
        if error:
            flash(error, 'error')
            connection.close()
            return render_template('update.html', agent=agent, codename=codename, username=username, pass_key=pass_key, password=password)
            
        try:
            # 7. COMMENT: Form alteration submission handler - override existing matching table data parameters securely.
            connection.execute(
                "UPDATE agents SET codename = ?, username = ?, pass_key = ?, password = ? WHERE id = ?",
                (codename, username, pass_key, password, agent_id)
            )
            connection.commit()
            flash("⚡ Classified credentials successfully overridden in core frame.", 'success')
            return redirect(url_for('profile', agent_id=agent_id))
        except Exception:
            flash("⚠️ Edit Rejected: That username is already assigned to another operative.", 'error')
        finally:
            connection.close()
            
    else:
        connection.close()
        
    return render_template('update.html', agent=agent)

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)
