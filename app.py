from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize the database and create the table
def init_db():
    conn = sqlite3.connect("vehicle.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY,  -- ID column as primary key
            name TEXT NOT NULL,      -- Name column
            brand TEXT NOT NULL,     -- Brand column
            fuel_type TEXT NOT NULL   -- Fuel Type column
        );
    ''')
    conn.commit()
    conn.close()

# Call the database initialization
init_db()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/adminlogin')
def admin_login():
    return render_template('adminlogin.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'sri' and password == '12345':
        return redirect(url_for('index'))
    else:
        return "Invalid credentials", 401

@app.route('/adminlogin', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'vishal' and password == '54321':
        session['user'] = 'admin'  # Set session user as admin
        return redirect(url_for('admin'))  # Redirect to admin page
    else:
        return "Invalid credentials", 401

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    vehicle_id = request.form.get('id')
    name = request.form.get('name')
    brand = request.form.get('brand')
    fuel_type = request.form.get('fuel-type')

    print(f"ID: {vehicle_id}, Name: {name}, Brand: {brand}, Fuel Type: {fuel_type}")

    try:
        conn = sqlite3.connect("vehicle.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (id, name, brand, fuel_type) VALUES (?, ?, ?, ?)
        ''', (vehicle_id, name, brand, fuel_type))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Vehicle with ID {vehicle_id} already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    return render_template('index.html', id=vehicle_id, name=name, brand=brand, fuel_type=fuel_type)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in
    
    search_query = request.args.get('search', '')
    conn = sqlite3.connect("vehicle.db")
    cursor = conn.cursor()

    if search_query:
        cursor.execute("SELECT * FROM vehicles WHERE name LIKE ? OR brand LIKE ?", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("SELECT * FROM vehicles")
    
    vehicles = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', vehicles=vehicles, search_query=search_query)

@app.route('/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    try:
        conn = sqlite3.connect("vehicle.db")
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM vehicles WHERE id = ?
        ''', (vehicle_id,))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
