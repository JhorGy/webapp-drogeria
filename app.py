from flask import Flask, render_template, request, redirect, url_for, current_app, session, abort
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.secret_key = 'tu-clave-secreta-aqui'
	app.config['TESTING'] = False
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/farmacia'

	db = SQLAlchemy(app)

	# Definición de los modelos de la base de datos
	class Product(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(50), nullable=False)
		description = db.Column(db.String(100))
		price = db.Column(db.Float, nullable=False)

	class Client(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		name = db.Column(db.String(50), nullable=False)
		email = db.Column(db.String(50), nullable=False)

	class User(db.Model):
		__tablename__ = 'users'
		id = db.Column(db.Integer, primary_key=True)
		username = db.Column(db.String(20), nullable=False)
		password = db.Column(db.String(20), nullable=False)
		role = db.Column(db.String(20), nullable=False) 

	def __init__(self, username, password, role):
		self.username = username
		self.password = password
		self.role = role


	# Rutas

	# Decorador para verificar si el usuario ha iniciado sesión
	def login_required(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if 'username' not in session:
				# Si el usuario no ha iniciado sesión, redirigir al formulario de inicio de sesión
				return redirect(url_for('login'))
			return f(*args, **kwargs)
		return decorated_function

	@app.route('/')
	def inicio():
		return render_template('login.html')


	@app.route('/index')
	@login_required
	def index():
		return render_template('index.html')



	@app.route('/login', methods=['GET', 'POST'])
	def login():
		error = None  # Variable para almacenar el mensaje de error
		
		if request.method == 'POST':
			username = request.form['username']
			password = request.form['password']
			
			# Verificar las credenciales del usuario en la base de datos
			user = User.query.filter_by(username=username, password=password).first()

			if user:
				# Autenticación exitosa, redirigir según el valor del rol
				if user.role == 1:
					session['username'] = username
					session['role'] = user.role
					return render_template('indexVendedor.html')
				elif user.role == 2:
					session['username'] = username
					session['role'] = user.role
					return render_template('index.html') 
				else:
					# Rol no reconocido, mostrar mensaje de error
					error = 'Rol no válido. Contacta al administrador.'
			else:
				# Autenticación fallida, mostrar un mensaje de error
				error = 'Credenciales inválidas. Inténtalo de nuevo.'

		# Método GET o error en la autenticación, mostrar el formulario de inicio de sesión
		return render_template('login.html', error=error)


		
		# Método GET, mostrar el formulario de inicio de sesión
		return render_template('login.html' , error=error)
			
		#     # Verificar las credenciales del usuario en la base de datos
		#     user = User.query.filter_by(username=username, password=password).first()
		#     if user:
		#         # Autenticación exitosa, redirigir al índice
		#         session['username'] = username
		#         return redirect(url_for('index'))
		#     else:
		#         # Autenticación fallida, mostrar un mensaje de error
		#         error = 'Credenciales inválidas. Inténtalo de nuevo.'
		#         return render_template('login.html', error=error)
		
		# # Método GET, mostrar el formulario de inicio de sesión
		# return render_template('login.html')

	@app.route('/logout')
	@login_required
	def logout():
		# Eliminar la sesión del usuario
		session.pop('username', None)
		return redirect(url_for('login'))

	@app.route('/dashboard')
	@login_required
	def dashboard():
		if 'user_id' not in session:
			return redirect(url_for('login'))

		user_id = session['user_id']
		user = User.query.get(user_id)

		if user.role == 'admin':
			# Lógica para el panel de administrador
			return render_template('admin_dashboard.html')
		else:
			# Lógica para el panel de usuario regular
			return render_template('user_dashboard.html')

	# Rutas para productos
	@app.route('/products')
	@login_required
	def products():
		products = Product.query.all()
		return render_template('products.html', products=products)

	@app.route('/add_product', methods=['GET', 'POST'])
	@login_required
	def add_product():
		if request.method == 'POST':
			name = request.form['name']
			description = request.form['description']
			price = request.form['price']
			product = Product(name=name, description=description, price=price)
			db.session.add(product)
			db.session.commit()
			return redirect('/products')
		return render_template('add_product.html')

	@app.route('/delete_product/<int:product_id>')
	@login_required
	def delete_product(product_id):
		with app.app_context():
			product = Product.query.get(product_id)
			db.session.delete(product)
			db.session.commit()
		return redirect('/products')

	@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
	@login_required
	def edit_product(product_id):
		product = Product.query.get(product_id)

		if request.method == 'POST':
			product.name = request.form['name']
			product.description = request.form['description']
			product.price = request.form['price']
			db.session.commit()
			return redirect('/products')

		return render_template('edit_product.html', product=product)


	# Rutas para clientes
	@app.route('/clients')
	@login_required
	def clients():
		clients = Client.query.all()
		return render_template('clients.html', clients=clients)

	@app.route('/add_client', methods=['GET', 'POST'])
	@login_required
	def add_client():
		if request.method == 'POST':
			name = request.form['name']
			email = request.form['email']
			client = Client(name=name, email=email)
			db.session.add(client)
			db.session.commit()
			return redirect('/clients')
		return render_template('add_client.html')

	@app.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
	@login_required
	def edit_client(client_id):
		client = Client.query.get(client_id)
		if request.method == 'POST':
			client.name = request.form['name']
			client.email = request.form['email']
			db.session.commit()
			return redirect('/clients')
		return render_template('edit_client.html', client=client)

	@app.route('/delete_client/<int:client_id>')
	@login_required
	def delete_client(client_id):
		with app.app_context():
			client = Client.query.get(client_id)
			db.session.delete(client)
			db.session.commit()
			return redirect('/clients')

	# Rutas para usuarios
	@app.route('/users')
	@login_required
	def users():
		if session['role'] == 1:
			abort(403)  # Devuelve un error 403 Forbidden si el rol es 1 (vendedor)
		users = User.query.all()
		return render_template('users.html', users=users)

	@app.route('/add_user', methods=['GET', 'POST'])
	@login_required
	def add_user():
		if request.method == 'POST':
			username = request.form['username']
			password = request.form['password']
			role = request.form['role']
			user = User(username=username, password=password, role=role)
			db.session.add(user)
			db.session.commit()
			return redirect('/users')
		return render_template('add_user.html')

	@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
	@login_required
	def edit_user(user_id):
		user = User.query.get(user_id)
		if request.method == 'POST':
			user.username = request.form['username']
			user.password = request.form['password']
			user.role = request.form['role']
			db.session.commit()
			return redirect('/users')
		return render_template('edit_user.html', user=user)

	@app.route('/delete_user/<int:user_id>')
	@login_required
	def delete_user(user_id):
		with app.app_context():
			user = User.query.get(user_id)
			db.session.delete(user)
			db.session.commit()
			return redirect('/users')
	
	with app.app_context():
		db.create_all()
	return app
	
if __name__ == '__main__':
	app = create_app()	
	app.run(debug=True)
