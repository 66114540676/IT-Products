from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # ถ้าพึ่งสร้าง User ให้สร้าง Profile ด้วย
    if created:
        Profile.objects.create(user=instance)
    else:
        # สำหรับ User เก่าที่อาจยังไม่มี Profile ให้สร้างให้เลย
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()