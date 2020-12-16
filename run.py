from app import create_db, db, bcrypt, create_app, utils
from app.models import (
    Post,
    User,
    Member,
    Group,
    Vote,
    Hide,
    Favourite,
    Role,
    Flag
)

app = create_app()

try:
    app.jinja_env.globals.update(__builtins__.__dict__) 
except Exception as err:
    app.jinja_env.globals.update(__builtins__)
     
app.jinja_env.globals.update(utils.__dict__)    


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Post": Post,
        "Vote": Vote,
        "Member": Member,
        "Group":Group,
        "Vote":Vote,
        "Hide":Hide,
        "Favourite":Favourite,
        "Role":Role,
        "Flag":Flag
    }

'''
if __name__ == '__main__':
    create_db()
    app.run(debug=True)
'''
