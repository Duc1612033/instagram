from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from django.forms import DateTimeField
from uuid import uuid4
import uuid


class Message(models.Model):
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    reciepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    body = models.TextField(null=True, blank=True)  # Có thể để trống nếu gửi ảnh
    image = models.ImageField(upload_to="media/messages/images", null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
   

    def sender_message(from_user, to_user, body=None, image=None):
        conversation_id = uuid4()

    # Tạo bản ghi tin nhắn cho người gửi
        sender_message = Message(
            user=from_user,
            sender=from_user,
            reciepient=to_user,
            body=body,
            image=image,
            conversation_id=conversation_id,
            is_read=True
        )
        sender_message.save()

        reciepient_message = Message(
            user=to_user,
            sender=from_user,
            reciepient=from_user,
            body=body,
            image=image,
            conversation_id=conversation_id,
            is_read=True
        )
        reciepient_message.save()
        return sender_message


    def get_message(user):
        users = []
        messages = Message.objects.filter(user=user).values('reciepient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['reciepient']),
                'last': message['last'],
                'unread': Message.objects.filter(user=user, reciepient__pk=message['reciepient'], is_read=False).count()
            })
        return users

    def update_conversation(self, new_body=None, new_image=None):
        # Cập nhật tất cả các tin nhắn trong cùng conversation_id
        updates = {}
        if new_body:
            updates["body"] = new_body
        if new_image:
            updates["image"] = new_image

        if updates:
            Message.objects.filter(conversation_id=self.conversation_id).update(**updates)

    def delete_message(message_id):
        Message.objects.filter(id=message_id).delete()

    @staticmethod
    def delete_message_pair(message_id):
        # Lấy tin nhắn ban đầu
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return False  # Tin nhắn không tồn tại

    # Xóa cả hai bản sao: của người gửi và người nhận
        Message.objects.filter(
            sender=message.sender,
            reciepient=message.reciepient,
            body=message.body,
            image=message.image,
        ).delete()

        Message.objects.filter(
            sender=message.reciepient,
            reciepient=message.sender,
            body=message.body,
            image=message.image,
        ).delete()

        return True

    def delete_message(self, user):
        """
        Deletes the message only if the user is the sender or recipient.
        """
        if self.sender == user or self.reciepient == user:
            self.delete()
            return True
        return False    
    
        
