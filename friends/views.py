# friends/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import FriendRequest, Friend
from django.contrib.auth.models import User
from authy.models import Profile
from .models import BlockedUser

from django.db.models import Q





def search_friends(request):
    query = request.GET.get('q', '')
    if query:
        # Tìm bạn bè theo tên người dùng
        friends = Friend.objects.filter(user__username__icontains=query)
        
        # Loại bỏ trùng lặp bằng cách sử dụng set để đảm bảo không trùng bạn bè
        seen_users = set()
        unique_friends = []

        for friend in friends:
            if friend.user.username not in seen_users:
                unique_friends.append(friend)
                seen_users.add(friend.user.username)
                
    else:
        unique_friends = []
    
    return render(request, 'friends/search_results.html', {'friends': unique_friends, 'query': query})



@login_required
def send_or_cancel_friend_request(request, user_id):
    user = get_object_or_404(User, id=user_id)
    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=request.user, to_user=user
    )

    if not created:
        # Nếu đã tồn tại, xóa yêu cầu (tức là "Cancel Invitation")
        friend_request.delete()

    return redirect('profile', username=user.username)  #

@login_required
def send_friend_request(request, user_id):
    user = User.objects.get(id=user_id)  # lấy user từ user_id
    # thêm logic gửi yêu cầu kết bạn ở đây
    return redirect('profile', username=user.username)


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    # Tạo mối quan hệ bạn bè cho cả hai người dùng
    Friend.objects.create(user=friend_request.from_user, friend=friend_request.to_user)
    Friend.objects.create(user=friend_request.to_user, friend=friend_request.from_user)
    
    # Xóa yêu cầu kết bạn sau khi chấp nhận
    friend_request.delete()
    
    return redirect('list_friends')


@login_required
def delete_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('friend_requests')



@login_required
def friend_requests(request):
    if request.user.is_authenticated:
        # Lấy danh sách yêu cầu kết bạn kèm theo thông tin hồ sơ của người gửi
        received_requests = FriendRequest.objects.filter(to_user=request.user).select_related('from_user__profile')
        return render(request, 'friends/friends_request.html', {'friend_requests': received_requests})
    else:
        return redirect('index')



def profile_view(request, username):
    # Logic để lấy dữ liệu người dùng theo username
    context = {
        'username': username,
        # Bạn có thể thêm các dữ liệu khác cần thiết để truyền vào template
    }
    return render(request, 'friends/profile.html', context)


@login_required
def list_friends(request):
    if request.user.is_authenticated:
        # Lọc danh sách bạn bè nhưng loại bỏ chính tài khoản người dùng
        friends = Friend.objects.filter(user=request.user).exclude(friend=request.user).select_related('friend__profile')
        return render(request, 'friends/list_friends.html', {'friends': friends})
    else:
        return redirect('sign-in')


@login_required
def unfriend(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Xóa bạn bè cho cả hai người dùng
    Friend.objects.filter(user=request.user, friend=user).delete()
    Friend.objects.filter(user=user, friend=request.user).delete()
    
    return redirect('profile', username=user.username)


@login_required
def block_friend(request, user_id):
    blocked_user = get_object_or_404(User, id=user_id)
    # Kiểm tra xem người dùng đã bị block chưa
    if not BlockedUser.objects.filter(user=request.user, blocked_user=blocked_user).exists():
        BlockedUser.objects.create(user=request.user, blocked_user=blocked_user)
    return redirect('list_block_friends')




@login_required
def unblock_friend(request, blocked_user_id):
    blocked_user = get_object_or_404(BlockedUser, id=blocked_user_id)
    if blocked_user.user == request.user:
        blocked_user.delete()
    return redirect('list_block_friends')

@login_required
def list_block_friends(request):
    blocked_users = BlockedUser.objects.filter(user=request.user)
    context = {
        'blocked_users': blocked_users
    }
    return render(request, 'friends/list_block_friends.html', context)


