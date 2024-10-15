from django.db.models.signals import post_save
from django.dispatch import receiver

from missions.models import Mission  
from .models import MinorCategory  


@receiver(post_save, sender=MinorCategory)
def create_default_missions(sender, instance, created, **kwargs):
    """
    MinorCategory가 생성될 때 자동으로 4개의 기본 Mission 객체를 생성하는 함수.
    
    새로운 MinorCategory가 생성되면, 해당 카테고리에 중간고사 및 기말고사 미션을 자동으로 생성합니다.
    각 미션은 5지선다형 문제와 코드 제출형 문제로 구성됩니다.

    Args:
        sender (type): MinorCategory 모델.
        instance (MinorCategory): 생성된 MinorCategory 인스턴스.
        created (bool): 새롭게 생성된 객체인지 여부.
        **kwargs: 추가적인 키워드 인자.
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
