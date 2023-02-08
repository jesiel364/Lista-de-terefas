from flask import Flask, render_template, request, redirect, flash, url_for, session
from markupsafe import escape
import sqlite3 as sql
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer
from models.forms import LoginForm
from horaData import t, hoje, simples, Tempo
import pyrebase

# FIREBASE CONFIG
config = {
      'apiKey': "AIzaSyDDQXepg6eW_fygTg6_LM9t1eVPhTvULDc",
      'authDomain': "lista-de-tarefas-c7323.firebaseapp.com",
      'databaseURL': "https://lista-de-tarefas-c7323-default-rtdb.firebaseio.com",
      'projectId': "lista-de-tarefas-c7323",
      'storageBucket': "lista-de-tarefas-c7323.appspot.com",
      'messagingSenderId': "302470237725",
      'appId': "1:302470237725:web:f0e82f04371de15a4e40f4",
      'measurementId': "G-RR9LLY7NB2"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db =  firebase.database()


# FLASK CONFIG
app = Flask(__name__)
notifications = ['verifique seu email']
app.secret_key='12345'


# ROTAS
@app.route('/')
def index():
    if('user' in session):
        if('user' in session):
            tasks = db.child('tarefas').get()
            for task in tasks.each():
                if task.val()['usuario']== session['user']:
                    tarefas = task
            # tarefas = session_sq.query(Tarefas).filter_by(usuario= session['user']).order_by(-Tarefas.id)
        else:
            tasks = db.child('tarefas').get()
            tarefas = tasks

        # Firebase
        pyre = db.child('tarefas').order_by_key().get()
    
    
        return render_template('home.html', hoje = int(hoje), pyre = pyre)
    else:
        return render_template('login.html')

@app.route('/', methods=['POST', 'GET'])
def salvar():
    if request.method == 'POST':
        titulo_text = request.form['titulo']
        if not titulo_text:
            flash( 'O campo tarefa é necessário !!', 'danger')
            return redirect(url_for('index'))
        if('user' in session):            
            data =  {
                
                'titulo': titulo_text,
                'concluido': 'false',
                'created_at': simples,
                'usuario': session['user']
            }
        else:
            flash('Atenção, as tarefas serão salvas temporariamente, recomendamos fazer o login.', 'danger')
            data =  {
                
                'titulo': titulo_text,
                'concluido': 'false',
                'created_at': simples
            }

        # firebase
        db.child('tarefas').push(data, session['idToken'])
        
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/delete/<string:key>', methods=['POST', 'GET'])
def delete(key):
    #firebase
    pyre = db.child('tarefas').get()
    
    db.child('tarefas').child(key).remove()
    return redirect(url_for('index'))
        
@app.route('/update/<string:key>', methods=['POST', 'GET'] )
def update(key):
    tarefa = db.child('tarefas').child(key).get()
    if tarefa.val()['concluido'] == 'false':
        db.child('tarefas').child(key).update({'concluido': 'true'})
    else:
            db.child('tarefas').child(key).update({'concluido': 'false'})
                
    return  redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if('user' in session):
        flash(f"Você já está logado",'warning')
        redirect(url_for('index'))
    else:
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            
            try:
                user = auth.create_user_with_email_and_password(email, senha)
                flash('Conta criada', 'success')
                session['user'] = email
                return redirect(url_for('index'))
            except:
                flash('Falha ao logar', 'danger')
                return render_template('home.html') 
    
    return render_template('register.html')
    
@app.route('/login', methods= ['POST', 'GET'])
def login():
    if('user' in session):
        flash(f"Olá, {session['user']}", "success")
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        try:
            user = auth.sign_in_with_email_and_password(email, senha)
            session['user'] = email
            session['idToken'] = user['idToken']
            return redirect(url_for('index'))
        except:
            flash('Email ou senha incorretos!', 'danger')
            return redirect(url_for('login')) 
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user')
    flash('Deslogado!', 'warning')
    return redirect('/')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html', perfil = session['user'])

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=8080)
    
