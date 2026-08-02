"""
Interview answer service with AI feedback
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.interview import InterviewAnswer, InterviewQuestion
from app.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class InterviewAnswerService:
    """Service for managing interview answers"""

    @staticmethod
    def submit_answer(
        db: Session,
        question_id: uuid.UUID,
        user_answer: str,
        answer_time_seconds: Optional[int] = None,
    ) -> InterviewAnswer:
        """Submit an answer to a question"""
        try:
            question = (
                db.query(InterviewQuestion)
                .filter(InterviewQuestion.id == question_id)
                .first()
            )
            if not question:
                raise ValueError("Question not found")

            # Delete existing answer if any
            existing = (
                db.query(InterviewAnswer)
                .filter(InterviewAnswer.question_id == question_id)
                .first()
            )
            if existing:
                db.delete(existing)

            answer = InterviewAnswer(
                question_id=question_id,
                user_answer=user_answer,
                answer_time_seconds=answer_time_seconds,
            )

            db.add(answer)
            db.commit()
            db.refresh(answer)

            logger.info(f"Submitted answer for question {question_id}")
            return answer
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting answer: {str(e)}")
            raise ValueError(f"Failed to submit answer: {str(e)}")

    @staticmethod
    def get_answer(db: Session, answer_id: uuid.UUID) -> Optional[InterviewAnswer]:
        """Get answer by ID"""
        try:
            return (
                db.query(InterviewAnswer)
                .filter(InterviewAnswer.id == answer_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving answer: {str(e)}")
            raise ValueError(f"Failed to retrieve answer: {str(e)}")

    @staticmethod
    def get_question_answer(
        db: Session, question_id: uuid.UUID
    ) -> Optional[InterviewAnswer]:
        """Get answer for a question"""
        try:
            return (
                db.query(InterviewAnswer)
                .filter(InterviewAnswer.question_id == question_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Error retrieving answer: {str(e)}")
            raise ValueError(f"Failed to retrieve answer: {str(e)}")

    @staticmethod
    def evaluate_answer(
        db: Session,
        answer_id: uuid.UUID,
        question_text: str,
    ) -> InterviewAnswer:
        """Evaluate answer using AI and store feedback"""
        try:
            answer = (
                db.query(InterviewAnswer)
                .filter(InterviewAnswer.id == answer_id)
                .first()
            )
            if not answer:
                raise ValueError("Answer not found")

            # Get AI evaluation
            provider = OpenAIProvider()
            evaluation_prompt = f"""
Evaluate this interview answer on a scale of 0-100.

Question: {question_text}

Answer: {answer.user_answer}

Provide your evaluation in this exact format:
SCORE: [0-100]
FEEDBACK: [brief feedback]
STRENGTHS: [comma-separated list of strengths]
IMPROVEMENTS: [comma-separated list of improvements]
            """

            response = provider.generate_text(
                prompt=evaluation_prompt,
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=300,
            )

            # Parse response
            lines = response.split("\n")
            score = 70
            feedback = "Good answer"
            strengths = "Clear communication"
            improvements = "Add more examples"

            for line in lines:
                if line.startswith("SCORE:"):
                    try:
                        score = int(line.split(":")[1].strip())
                    except:
                        pass
                elif line.startswith("FEEDBACK:"):
                    feedback = line.split(":", 1)[1].strip()
                elif line.startswith("STRENGTHS:"):
                    strengths = line.split(":", 1)[1].strip()
                elif line.startswith("IMPROVEMENTS:"):
                    improvements = line.split(":", 1)[1].strip()

            # Store evaluation
            answer.score = score
            answer.feedback = feedback
            answer.strengths = strengths
            answer.improvements = improvements
            answer.ai_model = "gpt-3.5-turbo"

            db.commit()
            db.refresh(answer)

            logger.info(f"Evaluated answer {answer_id} with score {score}")
            return answer
        except Exception as e:
            db.rollback()
            logger.error(f"Error evaluating answer: {str(e)}")
            raise ValueError(f"Failed to evaluate answer: {str(e)}")

    @staticmethod
    def get_session_answers(
        db: Session, session_id: uuid.UUID
    ) -> list[InterviewAnswer]:
        """Get all answers for a session"""
        try:
            from app.models.interview import InterviewSession

            session = (
                db.query(InterviewSession)
                .filter(InterviewSession.id == session_id)
                .first()
            )
            if not session:
                raise ValueError("Session not found")

            answers = (
                db.query(InterviewAnswer)
                .join(InterviewQuestion)
                .filter(InterviewQuestion.session_id == session_id)
                .all()
            )

            return answers
        except Exception as e:
            logger.error(f"Error retrieving answers: {str(e)}")
            raise ValueError(f"Failed to retrieve answers: {str(e)}")
