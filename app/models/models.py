from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Integer, nullable=False) 
    recommend = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<Feedback user_id={self.user_id} rating={self.rating}>"
