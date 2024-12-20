from django.db import models
from django.conf import settings

class Notification(models.Model):
    
    NOTIFICATION_TYPES = (
        ('message', 'message'),
        ('friend_request', 'friend_request'),
        ('game_challenge', 'game_challenge'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return f"{self.user} - {self.notification_type}"
