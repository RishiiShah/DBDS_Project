from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from models import db


class Question(db.Model):
    """
    A question posted by an end-user to customer service.
    """
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum('open', 'answered', 'closed', name='question_status'),
        default='open',
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = db.relationship('User', back_populates='questions')
    answers = db.relationship('Answer', back_populates='question',
                              cascade='all, delete-orphan', lazy='joined')

    def __repr__(self):
        return f'<Question "{self.subject}" by User #{self.user_id}>'


class Answer(db.Model):
    """
    A response from a customer representative to a user question.
    """
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('questions.id'), nullable=False
    )
    rep_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    question = db.relationship('Question', back_populates='answers')
    rep = db.relationship('User')

    def __repr__(self):
        return f'<Answer to Question #{self.question_id} by Rep #{self.rep_id}>'
