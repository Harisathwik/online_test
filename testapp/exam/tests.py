from django.utils import unittest
from exam.models import User, Profile, Question, Quiz, QuestionPaper,\
QuestionSet, AnswerPaper


class ModelsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """ Initial fixtures for testing environment"""

        # create user profile
        self.user = User.objects.create_user(username='demo_user',
                                             password='demo',
                                             email='demo@test.com')
        self.profile = Profile.objects.create(user=self.user, roll_number=1,
                                              institute='IIT',
                                              department='Chemical',
                                              position='Student')

        # create 20 questions
        for i in range(1, 21):
            Question.objects.create(summary='Q%d' % (i))

        # All active questions
        self.questions = Question.objects.filter(active=True)

        # Single question details
        self.question = self.questions[0]
        self.question.summary = 'Demo question'
        self.question.language = 'Python'
        self.question.type = 'Code'
        self.question.options = None
        self.question.description = 'Write a function'
        self.question.points = 1.0
        self.question.active = True
        self.question.test = 'Test Cases'
        self.question.snippet = 'def myfunc()'
        self.question.tags.add('python', 'function')

        # create a quiz
        self.quiz = Quiz.objects.create(start_date='2014-06-16',
                                        duration=30, active=False,
                                        description='demo quiz')

        # create question paper
        self.quest_paper = QuestionPaper.objects.create(quiz=self.quiz,
                                                        total_marks=0.0)

        # add fixed set of questions to the question paper
        self.quest_paper.fixed_questions.add(self.questions[3],
                                             self.questions[5])

        # create two QuestionSet for random questions
        # QuestionSet 1
        self.quest_set_1 = QuestionSet.objects.create(marks=2, num_questions=2)

        # add pool of questions for random sampling
        self.quest_set_1.questions.add(self.questions[6], self.questions[7],
                                       self.questions[8], self.questions[9])

        # add question set 1 to random questions in Question Paper
        self.quest_paper.random_questions.add(self.quest_set_1)

        # QuestionSet 2
        self.quest_set_2 = QuestionSet.objects.create(marks=3, num_questions=3)

        # add pool of questions
        self.quest_set_2.questions.add(self.questions[11], self.questions[12],
                                       self.questions[13], self.questions[14])

        # add question set 2
        self.quest_paper.random_questions.add(self.quest_set_2)

        # ip address for AnswerPaper
        self.ip = '127.0.0.1'

        # create answerpaper
        self.answerpaper = AnswerPaper(user=self.user, profile=self.profile,
                                       questions='1|2|3',
                                       question_paper=self.quest_paper,
                                       start_time='2014-06-13 12:20:19.791297',
                                       end_time='2014-06-13 12:50:19.791297',
                                       user_ip=self.ip)

###############################################################################
    def test_user_profile(self):
        """ Test user profile"""
        self.assertIs(type(self.profile), type(Profile()))
        self.assertEqual(self.user.username, 'demo_user')
        self.assertEqual(self.profile.user.username, 'demo_user')
        self.assertEqual(self.profile.roll_number, 1)
        self.assertEqual(self.profile.institute, 'IIT')
        self.assertEqual(self.profile.department, 'Chemical')
        self.assertEqual(self.profile.position, 'Student')

    def test_question(self):
        """ Test question """
        self.assertIs(type(self.question), type(Question()))
        self.assertEqual(self.question.summary, 'Demo question')
        self.assertEqual(self.question.language, 'Python')
        self.assertEqual(self.question.type, 'Code')
        self.assertTrue(self.question.options is None)
        self.assertEqual(self.question.description, 'Write a function')
        self.assertEqual(self.question.points, 1.0)
        self.assertTrue(self.question.active)
        self.assertEqual(self.question.test, 'Test Cases')
        self.assertEqual(self.question.snippet, 'def myfunc()')
        tag_list = []
        for tag in self.question.tags.all():
            tag_list.append(tag.name)
        self.assertEqual(tag_list, ['python', 'function'])
        self.assertEqual(len(self.questions), 20)

    def test_quiz(self):
        """ Test Quiz"""
        self.assertIs(type(self.quiz), type(Quiz()))
        self.assertEqual(self.quiz.start_date, '2014-06-16')
        self.assertEqual(self.quiz.duration, 30)
        self.assertTrue(self.quiz.active is False)
        self.assertEqual(self.quiz.description, 'demo quiz')

    def test_questionpaper(self):
        """ Test question paper"""
        self.assertIs(type(self.quest_paper), type(QuestionPaper()))
        self.assertEqual(self.quest_paper.quiz.description, 'demo quiz')
        self.assertEqual(list(self.quest_paper.fixed_questions.all()),
                         [self.questions[3], self.questions[5]])

    def test_get_random_questions(self):
        """ Test get_random_questions() method of Question Paper  """
        random_questions_set_1 = set(self.quest_set_1.get_random_questions())
        random_questions_set_2 = set(self.quest_set_2.get_random_questions())

        # To check whether random questions are from random_question_set
        boolean = set(self.quest_set_1.questions.all()).\
                  intersection(random_questions_set_1)\
                  == random_questions_set_1
        self.assertTrue(boolean)
        self.assertEqual(len(random_questions_set_1), 2)
        self.assertFalse(random_questions_set_1 == random_questions_set_2)

    def test_get_questions_for_answerpaper(self):
        """ Test get_questions_for_answerpaper() method of Question Paper"""
        questions = self.quest_paper._get_questions_for_answerpaper()
        fixed = list(self.quest_paper.fixed_questions.all())
        quest_set = self.quest_paper.random_questions.all()
        total_random_questions = 0
        available_questions = []
        for qs in quest_set:
            total_random_questions += qs.num_questions
            available_questions += qs.questions.all()
        self.assertEqual(total_random_questions, 5)
        self.assertEqual(len(available_questions), 8)
        self.assertEqual(len(questions), 7)

    def test_make_answerpaper(self):
        """ Test make_answerpaper() method of Question Paper"""
        answerpaper = self.quest_paper.make_answerpaper(self.user,
                                                        self.profile, self.ip)
        self.assertIs(type(answerpaper), type(AnswerPaper()))
        paper_questions = set((answerpaper.questions).split('|'))
        self.assertEqual(len(paper_questions), 7)
        fixed = {'4', '6'}
        boolean = fixed.intersection(paper_questions) == fixed
        self.assertTrue(boolean)

    def test_answerpaper(self):
        """ Test Answer Paper"""
        self.assertIs(type(self.answerpaper), type(AnswerPaper()))
        self.assertEqual(self.answerpaper.user.username, 'demo_user')
        self.assertEqual(self.answerpaper.profile_id, 1)
        self.assertEqual(self.answerpaper.user_ip, self.ip)
        questions = self.answerpaper.questions
        num_questions = len(questions.split('|'))
        self.assertEqual(questions, '1|2|3')
        self.assertEqual(num_questions, 3)
        self.assertEqual(self.answerpaper.question_paper, self.quest_paper)
        self.assertEqual(self.answerpaper.question_paper, self.quest_paper)
        self.assertEqual(self.answerpaper.start_time,
                         '2014-06-13 12:20:19.791297')
        self.assertEqual(self.answerpaper.end_time,
                         '2014-06-13 12:50:19.791297')

    def test_current_question(self):
        """ Test current_question() method of Answer Paper"""
        current_question = self.answerpaper.current_question()
        self.assertTrue(current_question is not None)

    def test_completed_question(self):
        """ Test completed_question() method of Answer Paper"""
        question = self.answerpaper.completed_question(3)
        self.assertTrue(question is not None)
        self.assertEqual(self.answerpaper.questions_left(), 2)

    def test_questions_left(self):
        """ Test questions_left() method of Answer Paper"""
        self.assertEqual(self.answerpaper.questions_left(), 2)

    def test_skip(self):
        """ Test skip() method of Answer Paper"""
        self.assertTrue(self.answerpaper.skip() is not None)

    def test_answered_str(self):
        """ Test answered_str() method of Answer Paper"""
        self.assertEqual(self.answerpaper.get_answered_str(), 'None')

    def test_get_marks_obtained(self):
        """ Test get_marks_obtained() method of Answer Paper"""
        self.assertEqual(self.answerpaper.get_marks_obtained(), 0)

    def test_get_question_answer(self):
        """ Test get_question_answer() method of Answer Paper"""
        self.assertEqual(self.answerpaper.get_question_answers(), {})
