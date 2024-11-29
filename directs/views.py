
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from directs.models import Message
from django.contrib.auth.models import User
from authy.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from .forms import MessageForm
from django.http import JsonResponse
@login_required
def delete_message(request, message_id):
    """
    Deletes a message if the user is the sender or recipient.
    """
    # Get the message object
    message = get_object_or_404(Message, id=message_id)

    # Check if the logged-in user is the sender or recipient
    if message.delete_message(request.user):
        # Redirect to the previous page or message list page
        return redirect('directs', username=to_user.username)  # Adjust this URL as needed
    else:
        # Show an error message if the user is not authorized to delete
        return render(request, 'error.html', {'message': "You are not authorized to delete this message."})


def delete_message_view(request, message_id):
    try:
        # Lấy tin nhắn gốc
        message = Message.objects.get(id=message_id)

        # Xóa tất cả các tin nhắn thuộc cùng conversation_id
        Message.objects.filter(conversation_id=message.conversation_id).delete()

        # Chuyển hướng về danh sách tin nhắn
        return redirect('directs', username=request.user.username)
    except Message.DoesNotExist:
        print("Tin nhắn không tồn tại!")
        return redirect('directs', username=request.user.username)


def send_directs(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            to_user = User.objects.get(username=request.POST.get('to_user'))
            body = form.cleaned_data.get('body')
            image = form.cleaned_data.get('image')
            Message.sender_message(from_user=request.user, to_user=to_user, body=body, image=image)
            return redirect('directs', username=to_user.username)
    return redirect('directs')


from django.http import HttpResponseForbidden

def update_message(request, message_id):
    # Lấy tin nhắn gốc
    message = get_object_or_404(Message, id=message_id)

    # Kiểm tra quyền chỉnh sửa
    if request.user != message.sender:
        return HttpResponseForbidden("Bạn không có quyền chỉnh sửa tin nhắn này.")

    if request.method == "POST":
        new_body = request.POST.get("body")  # Lấy nội dung văn bản
        if new_body:
            message.body = new_body

        # Kiểm tra nếu có tệp ảnh mới được tải lên
        if "image" in request.FILES:
            new_image = request.FILES["image"]
            message.image = new_image

        # Lưu lại tin nhắn
        message.save()

        # Cập nhật tất cả các tin nhắn liên quan theo conversation_id
        Message.objects.filter(conversation_id=message.conversation_id).update(
            body=message.body,
            image=message.image
        )

        # Điều hướng về trang danh sách tin nhắn
        return redirect("directs", username=request.user.username)

    return render(request, "directs/update_message.html", {"message": message})




@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == "POST":
        message.delete()
        return redirect('directs', username=message.reciepient.username)
    context = {
        'message': message
    }
    return render(request, 'directs/delete_message.html', context)



def search_all(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', '')
    if search_type == 'friends':
        return redirect(f'/friends/search/?q={query}')
    elif search_type == 'groups':
        return redirect(f'/groups/search/?q={query}')
    elif search_type == 'pages':
        return redirect(f'/pages/search/?q={query}')
    elif search_type == 'posts':
        return redirect(f'/posts/search/?q={query}')
    return redirect('index')

@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    profile = get_object_or_404(Profile, user=user)

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
    context = {
        'directs':directs,
        'messages': messages,
        'active_direct': active_direct,
        'profile': profile,
    }
    return render(request, 'directs/direct.html', context)


@login_required
def Directs(request, username):
    user  = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)  
    directs.update(is_read=True)

    for message in messages:
            if message['user'].username == username:
                message['unread'] = 0
    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }
    return render(request, 'directs/direct.html', context)



def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Paginator
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
            }

    return render(request, 'directs/search.html', context)

def NewConversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('search-users')
    if from_user != to_user:
        Message.sender_message(from_user, to_user, body)
    return redirect('message')
