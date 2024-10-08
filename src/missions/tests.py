from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from courses.models import MajorCategory,MinorCategory
from .models import (
    Mission,
    Question,
    MultipleChoiceOption,
    CodeQuestion,
    MissionSubmission,
    MultipleChoiceSubmission,
    CodeSubmission,
)

User = get_user_model()


class MissionAPITestCase(APITestCase):
    def setUp(self):
        # 사용자 생성
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.user = User.objects.create_user(
            username='testuser', email='user@example.com', password='userpass'
        )

        # 대분류 카테고리 생성 (필요한 경우)
        self.major_category = MajorCategory.objects.create(
            name='Programming',
            order=1
        )

        # 소분류 카테고리 생성 (필수 필드 추가)
        self.minor_category = MinorCategory.objects.create(
            name='Python Basics',
            major_category=self.major_category,
            content='Python programming basics.',
            order=1
        )

        # 미션 생성
        self.mission = Mission.objects.create(
            minor_category=self.minor_category,
            title='Sample Mission',
            description='This is a sample mission.',
            mission_type='MID',
            order=1,
            passing_score=60,
        )

        # 5지선다형 문제 생성
        self.mcq_question = Question.objects.create(
            mission=self.mission,
            question_type='MCQ',
            content='파이썬에서 리스트를 생성하는 키워드는 무엇인가요?',
            order=1,
            points=10,
        )

        # 선택지 생성
        self.option1 = MultipleChoiceOption.objects.create(
            question=self.mcq_question, content='[]', is_correct=True, order=1
        )
        self.option2 = MultipleChoiceOption.objects.create(
            question=self.mcq_question, content='{}', is_correct=False, order=2
        )
        self.option3 = MultipleChoiceOption.objects.create(
            question=self.mcq_question, content='()', is_correct=False, order=3
        )
        self.option4 = MultipleChoiceOption.objects.create(
            question=self.mcq_question, content='<>', is_correct=False, order=4
        )
        self.option5 = MultipleChoiceOption.objects.create(
            question=self.mcq_question, content='//', is_correct=False, order=5
        )

        # 코드 제출형 문제 생성
        self.code_question = Question.objects.create(
            mission=self.mission,
            question_type='CODE',
            content='주어진 숫자가 짝수인지 확인하는 함수를 작성하세요.',
            order=2,
            points=20,
        )

        # 코드 문제의 추가 정보 생성
        self.code_question_detail = CodeQuestion.objects.create(
            question=self.code_question,
            initial_code='def is_even(n):\n    # 여기에 코드를 작성하세요.',
            test_cases=[
                {'input': [2], 'expected_output': True},
                {'input': [3], 'expected_output': False},
                {'input': [0], 'expected_output': True},
                {'input': [-2], 'expected_output': True},
            ],
        )

    def test_mission_list(self):
        """
        미션 목록 조회 테스트
        """
        url = reverse('mission-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mission_detail(self):
        """
        미션 상세 조회 테스트
        """
        url = reverse('mission-detail', args=[self.mission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Sample Mission')

    def test_mission_creation_by_admin(self):
        """
        관리자에 의한 미션 생성 테스트
        """
        self.client.login(username='admin', password='adminpass')
        url = reverse('mission-list')
        data = {
            'minor_category': self.minor_category.id,
            'title': 'New Mission',
            'description': 'New mission description.',
            'mission_type': 'FINAL',
            'order': 2,
            'passing_score': 70,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mission_creation_by_user(self):
        """
        일반 사용자가 미션을 생성할 수 없는지 테스트
        """
        self.client.login(username='testuser', password='userpass')
        url = reverse('mission-list')
        data = {
            'minor_category': self.minor_category.id,
            'title': 'Unauthorized Mission',
            'description': 'Should not be created.',
            'mission_type': 'MID',
            'order': 3,
            'passing_score': 50,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mission_submission(self):
        """
        미션 제출 및 채점 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mission_submission_id = response.data['id']

        # 객관식 문제 제출 (정답)
        url = reverse('multiplechoicesubmission-list')
        data = {
            'mission_submission': mission_submission_id,
            'question': self.mcq_question.id,
            'selected_option': self.option1.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 코드 문제 제출 (올바른 코드)
        url = reverse('codesubmission-list')
        submitted_code = '''
def is_even(n):
    return n % 2 == 0
'''
        data = {
            'mission_submission': mission_submission_id,
            'question': self.code_question.id,
            'submitted_code': submitted_code,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 미션 제출 결과 확인
        mission_submission = MissionSubmission.objects.get(id=mission_submission_id)
        self.assertTrue(mission_submission.is_passed)
        self.assertEqual(mission_submission.total_score, 30)

    def test_mission_submission_with_incorrect_answers(self):
        """
        오답으로 미션 제출 시 통과하지 못하는지 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        mission_submission_id = response.data['id']

        # 객관식 문제 제출 (오답)
        url = reverse('multiplechoicesubmission-list')
        data = {
            'mission_submission': mission_submission_id,
            'question': self.mcq_question.id,
            'selected_option': self.option2.id,
        }
        response = self.client.post(url, data, format='json')

        # 코드 문제 제출 (오답 코드)
        url = reverse('codesubmission-list')
        submitted_code = '''
def is_even(n):
    return False
'''
        data = {
            'mission_submission': mission_submission_id,
            'question': self.code_question.id,
            'submitted_code': submitted_code,
        }
        response = self.client.post(url, data, format='json')

        # 미션 제출 결과 확인
        mission_submission = MissionSubmission.objects.get(id=mission_submission_id)
        self.assertFalse(mission_submission.is_passed)
        self.assertEqual(mission_submission.total_score, 0)

    def test_duplicate_mission_submission(self):
        """
        동일한 미션에 대해 중복 제출이 불가능한지 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 첫 번째 제출
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 두 번째 제출 시도
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_option_submission(self):
        """
        다른 문제의 선택지를 제출할 경우 에러 발생 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        mission_submission_id = response.data['id']

        # 존재하지 않는 선택지 ID로 제출
        url = reverse('multiplechoicesubmission-list')
        data = {
            'mission_submission': mission_submission_id,
            'question': self.mcq_question.id,
            'selected_option': 9999,  # 존재하지 않는 ID
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_code_submission_syntax_error(self):
        """
        구문 오류가 있는 코드 제출 시 점수가 0인지 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        mission_submission_id = response.data['id']

        # 구문 오류가 있는 코드 제출
        url = reverse('codesubmission-list')
        submitted_code = '''
def is_even(n)
    return n % 2 == 0
'''  # 콜론 누락
        data = {
            'mission_submission': mission_submission_id,
            'question': self.code_question.id,
            'submitted_code': submitted_code,
        }
        response = self.client.post(url, data, format='json')

        # 제출 결과 확인
        code_submission = CodeSubmission.objects.get(
            mission_submission=mission_submission_id, question=self.code_question
        )
        self.assertEqual(code_submission.score, 0)

    def test_code_submission_runtime_error(self):
        """
        실행 중 예외가 발생하는 코드 제출 시 점수가 0인지 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        url = reverse('missionsubmission-list')
        data = {'mission': self.mission.id}
        response = self.client.post(url, data, format='json')
        mission_submission_id = response.data['id']

        # 실행 중 에러가 발생하는 코드 제출
        url = reverse('codesubmission-list')
        submitted_code = '''
def is_even(n):
    return n / 0  # ZeroDivisionError 발생
'''
        data = {
            'mission_submission': mission_submission_id,
            'question': self.code_question.id,
            'submitted_code': submitted_code,
        }
        response = self.client.post(url, data, format='json')

        # 제출 결과 확인
        code_submission = CodeSubmission.objects.get(
            mission_submission=mission_submission_id, question=self.code_question
        )
        self.assertEqual(code_submission.score, 0)

    def test_mission_submission_list(self):
        """
        미션 제출 목록 조회 테스트
        """
        self.client.login(username='testuser', password='userpass')

        # 미션 제출 생성
        MissionSubmission.objects.create(user=self.user, mission=self.mission)

        url = reverse('missionsubmission-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_permission_mission_submission(self):
        """
        다른 사용자의 미션 제출을 조회할 수 없는지 테스트
        """
        other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='otherpass'
        )
        MissionSubmission.objects.create(user=other_user, mission=self.mission)

        self.client.login(username='testuser', password='userpass')
        url = reverse('missionsubmission-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)
