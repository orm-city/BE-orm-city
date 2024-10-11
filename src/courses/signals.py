# courses/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from missions.models import Mission  # Mission 모델은 mission 앱에 속해 있음
from .models import MinorCategory  # MinorCategory는 courses 앱에 속해 있음


@receiver(post_save, sender=MinorCategory)
def create_default_missions(sender, instance, created, **kwargs):
    """
    MinorCategory가 생성될 때 자동으로 4개의 Mission 객체를 생성하는 함수.
    """
    if created:
        # 중간 미션 - 5지선다형
        Mission.objects.create(
            title="중간고사 5지선다형 미션",
            description="중간고사 5지선다형 문제에 대한 설명",
            minor_category=instance,
            mission_type="multiple_choice",
            is_midterm=True,
        )

        # 중간 미션 - 코드 제출형
        Mission.objects.create(
            title="중간고사 코드 제출형 미션",
            description="중간고사 코드 제출형 문제에 대한 설명",
            minor_category=instance,
            mission_type="code_submission",
            is_midterm=True,
        )

        # 기말 미션 - 5지선다형
        Mission.objects.create(
            title="기말고사 5지선다형 미션",
            description="기말고사 5지선다형 문제에 대한 설명",
            minor_category=instance,
            mission_type="multiple_choice",
            is_final=True,
        )

        # 기말 미션 - 코드 제출형
        Mission.objects.create(
            title="기말고사 코드 제출형 미션",
            description="기말고사 코드 제출형 문제에 대한 설명",
            minor_category=instance,
            mission_type="code_submission",
            is_final=True,
        )
