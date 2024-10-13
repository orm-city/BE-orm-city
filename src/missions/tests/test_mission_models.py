# import pytest
# from missions.models import Mission, MultipleChoiceQuestion, CodeSubmission, TestCase
# from django.contrib.auth import get_user_model

# User = get_user_model()


# @pytest.mark.django_db
# def test_mission_creation(minor_category):
#     """
#     Mission 모델 생성 테스트.
#     """
#     mission = Mission.objects.create(
#         title="Test Mission",
#         description="This is a test mission",
#         minor_category=minor_category,
#         mission_type="multiple_choice",
#         is_midterm=True,
#         is_final=False,
#     )

#     assert Mission.objects.count() == 1
#     assert mission.title == "Test Mission"
#     assert mission.mission_type == "multiple_choice"
#     assert mission.is_midterm is True
#     assert mission.is_final is False
#     assert str(mission) == f"{minor_category.name}-Test Mission"


# @pytest.mark.django_db
# def test_multiple_choice_question_creation(mission):
#     """
#     MultipleChoiceQuestion 모델 생성 테스트.
#     """
#     question = MultipleChoiceQuestion.objects.create(
#         mission=mission,
#         question="What is the capital of France?",
#         option_1="Paris",
#         option_2="Berlin",
#         option_3="Madrid",
#         option_4="Rome",
#         option_5="London",
#         correct_option=1,
#     )

#     assert MultipleChoiceQuestion.objects.count() == 1
#     assert question.question == "What is the capital of France?"
#     assert question.correct_option == 1
#     assert str(question) == "What is the capital of France?"


# @pytest.mark.django_db
# def test_code_submission_creation(mission):
#     """
#     CodeSubmission 모델 생성 테스트.
#     """
#     code_submission = CodeSubmission.objects.create(
#         mission=mission,
#         problem_statement="Write a function to reverse a string.",
#         example_input="'hello'",
#         example_output="'olleh'",
#         time_limit=2,
#         memory_limit=128,
#         language="python",
#     )

#     assert CodeSubmission.objects.count() == 1
#     assert code_submission.problem_statement == "Write a function to reverse a string."
#     assert code_submission.language == "python"
#     assert code_submission.time_limit == 2
#     assert code_submission.memory_limit == 128
#     assert str(code_submission) == "Write a function to reverse a string."


# @pytest.mark.django_db
# def test_test_case_creation(code_submission):
#     """
#     TestCase 모델 생성 테스트.
#     """
#     test_case = TestCase.objects.create(
#         code_submission=code_submission,
#         input_data="'abc'",
#         expected_output="'cba'",
#         is_sample=True,
#     )

#     assert TestCase.objects.count() == 1
#     assert test_case.input_data == "'abc'"
#     assert test_case.expected_output == "'cba'"
#     assert test_case.is_sample is True
#     assert str(test_case) == "입력: 'abc' / 예상 출력: 'cba'"


# @pytest.mark.django_db
# def test_multiple_choice_submission_creation(multiple_choice_question, user):
#     """
#     MultipleChoiceSubmission 모델 생성 테스트.
#     """
#     submission = MultipleChoiceQuestion.objects.create(
#         user=user, question=multiple_choice_question, selected_option=1, is_correct=True
#     )

#     assert MultipleChoiceQuestion.objects.count() == 1
#     assert submission.user == user
#     assert submission.selected_option == 1
#     assert submission.is_correct is True
#     assert str(submission) == f"{user.username} - {multiple_choice_question.question}"


# @pytest.mark.django_db
# def test_code_submission_record_creation(code_submission, user):
#     """
#     CodeSubmissionRecord 모델 생성 테스트.
#     """
#     submission_record = CodeSubmission.objects.create(
#         user=user,
#         code_submission=code_submission,
#         submitted_code="def reverse_string(s): return s[::-1]",
#         test_results="Passed",
#         result_summary="All tests passed",
#         is_passed=True,
#         execution_time=1.2,
#         memory_usage=1024,
#     )

#     assert CodeSubmission.objects.count() == 1
#     assert submission_record.user == user
#     assert submission_record.submitted_code == "def reverse_string(s): return s[::-1]"
#     assert submission_record.test_results == "Passed"
#     assert submission_record.is_passed is True
#     assert submission_record.execution_time == 1.2
#     assert submission_record.memory_usage == 1024
#     assert (
#         str(submission_record)
#         == f"{user.username} - {code_submission.problem_statement}"
#     )
