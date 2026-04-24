from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.support import Answer, Question
from utils.decorators import role_required

support_bp = Blueprint('support', __name__, url_prefix='/support')


# ── End-user: submit and view questions ──────────────────────────────────────

@support_bp.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'GET':
        return render_template('support/ask.html')

    subject = request.form.get('subject', '').strip()
    body    = request.form.get('body', '').strip()

    errors = []
    if not subject: errors.append('Subject is required.')
    if not body:    errors.append('Message body is required.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return render_template('support/ask.html', subject=subject, body=body)

    question = Question(
        user_id=current_user.id,
        subject=subject,
        body=body,
        status='open',
    )
    db.session.add(question)
    db.session.commit()

    flash('Your question has been submitted. A rep will reply soon.', 'success')
    return redirect(url_for('support.my_questions'))


@support_bp.route('/my-questions')
@login_required
def my_questions():
    questions = (
        Question.query
        .filter_by(user_id=current_user.id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return render_template('support/my_questions.html', questions=questions)


# ── Keyword search across public Q&A ─────────────────────────────────────────

@support_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    questions = []
    if q:
        pattern = f'%{q}%'
        questions = (
            Question.query
            .filter(
                Question.status == 'answered',
                db.or_(
                    Question.subject.ilike(pattern),
                    Question.body.ilike(pattern),
                )
            )
            .order_by(Question.created_at.desc())
            .all()
        )
    return render_template('support/search.html', questions=questions, q=q)


# ── Rep: view all open questions and reply ───────────────────────────────────

@support_bp.route('/questions')
@role_required('rep', 'admin')
def questions():
    status_filter = request.args.get('status', 'open')
    q = request.args.get('q', '').strip()

    query = Question.query
    if status_filter in ('open', 'answered', 'closed'):
        query = query.filter_by(status=status_filter)
    if q:
        pattern = f'%{q}%'
        query = query.filter(
            db.or_(
                Question.subject.ilike(pattern),
                Question.body.ilike(pattern),
            )
        )

    questions = query.order_by(Question.created_at.asc()).all()
    return render_template('rep/questions.html',
                           questions=questions,
                           status_filter=status_filter,
                           q=q)


@support_bp.route('/questions/<int:question_id>/reply', methods=['POST'])
@role_required('rep', 'admin')
def reply(question_id):
    question = Question.query.get_or_404(question_id)
    body = request.form.get('body', '').strip()

    if not body:
        flash('Reply cannot be empty.', 'error')
        return redirect(url_for('support.questions'))

    answer = Answer(
        question_id=question.id,
        rep_id=current_user.id,
        body=body,
    )
    db.session.add(answer)
    question.status = 'answered'
    db.session.commit()

    flash(f'Reply posted for question #{question_id}.', 'success')
    return redirect(url_for('support.questions'))


@support_bp.route('/questions/<int:question_id>/close', methods=['POST'])
@role_required('rep', 'admin')
def close_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.status = 'closed'
    db.session.commit()
    flash(f'Question #{question_id} closed.', 'success')
    return redirect(url_for('support.questions'))
