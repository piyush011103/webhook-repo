from flask import Flask, render_template
from routes.webhook import webhook
from routes.events import events

app = Flask(__name__)

app.register_blueprint(webhook)
app.register_blueprint(events)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
