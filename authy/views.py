from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login
from post.models import Post, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from datetime import timedelta
from django.utils import timezone
from friends.models import FriendRequest,Friend,BlockedUser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.http import HttpResponseBadRequest

def upload_cover_photo(request):
    if request.method == 'POST':
        user = request.user  # Lấy đối tượng User
        profile = user.profile  # Lấy Profile từ User
        print(user.username)  # Truy cập username từ User, không phải Profile
        profile.cover_photo = request.FILES.get('cover_photo')
        profile.save()
        return redirect('profile', username=request.user.username)  # Redirect sau khi lưu


@login_required
def TogglePrivacy(request):
    if request.method == 'POST':
        # Lấy hồ sơ của người dùng hiện tại
        profile = request.user.profile  
        # Cập nhật trạng thái riêng tư dựa trên form
        profile.is_private = 'is_private' in request.POST
        profile.save()
        return redirect('profile', username=request.user.username)
    return HttpResponseBadRequest("Invalid Request")


def follow_list(request, username, option):
    user = get_object_or_404(User, username=username)

    if option == "followers":
        follow_list = Follow.objects.filter(following=user).select_related('follower')
    elif option == "following":
        follow_list = Follow.objects.filter(follower=user).select_related('following')
    else:
        follow_list = []

    context = {
        'user': user,
        'follow_list': follow_list,
        'option': option,
    }
    return render(request, 'follow_list.html', context)




@login_required
def UserProfile(request, username):
    Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    user_profile = get_object_or_404(User, username=username)
    
    # Initialize variables to avoid UnboundLocalError
    is_friend = False
    posts = []

    # Check if the profile is private
    if profile.is_private and request.user != user:
        posts = []  # Don't show posts if the profile is private
    else:
        is_friend = Friend.objects.filter(user=request.user, friend=user).exists()
        posts = user_profile.post_set.all()
        
        # Filter posts based on privacy settings
        filtered_posts = []
        for post in posts:
            if post.privacy == 'only_me' and post.user == request.user:
                filtered_posts.append(post)
            elif post.privacy == 'friends' and (post.user == request.user or is_friend):
                filtered_posts.append(post)
            elif post.privacy == 'public':
                filtered_posts.append(post)
        posts = filtered_posts

    # Check if the user is blocked
    is_blocked = BlockedUser.objects.filter(user=request.user, blocked_user=user).exists()
    if is_blocked:
        return render(request, 'friends/profile_blocked.html')

    # Additional context
    friend_request_exists = FriendRequest.objects.filter(from_user=request.user, to_user=user).exists()
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    # Pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'posts': posts_paginator,
        'profile': profile,
        'posts_count': posts_count,
        'following_count': following_count,
        'followers_count': followers_count,
        'follow_status': follow_status,
        'friend_request_exists': friend_request_exists,
        'is_friend': is_friend,
        'is_blocked': is_blocked,
        'user_profile': user_profile,
    }
    return render(request, 'profile.html', context)



def EditProfile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)  # Thay đổi ở đây
        if form.is_valid():
            form.save()  # Lưu trực tiếp từ form
            print("Form is valid, profile updated.")  # In ra thông báo
            return redirect('profile', profile.user.username)  # Đảm bảo redirect tới profile
        else:
            print("Form errors:", form.errors)  # In ra lỗi nếu form không hợp lệ
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,  # Truyền profile vào context nếu cần
        
    }
    return render(request, 'editprofile.html', context)


def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # Profile.get_or_create(user=request.user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hurray your account was created!!')

            # Automatically Log In The User
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],)
            login(request, new_user)
            # return redirect('editprofile')
            return redirect('index')
            


    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'sign-up.html', context)


# views.py change password
@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('password_change_done')
    ##################################################
from django.http import JsonResponse

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Xóa tài khoản người dùng
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
    #####################################################
    #otp
   
from django.core.mail import send_mail

from .models import PasswordResetOTP

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = PasswordResetOTP(user=user)
            otp.generate_otp()
            
            send_mail(
                'Your OTP Code',
                f'Your OTP code is: {otp.otp_code}',
                'ductran26102k3@gmail.com',  # Thay đổi thành địa chỉ email của bạn
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp')  # Chuyển hướng tới trang xác minh OTP
        except User.DoesNotExist:
            return render(request, 'send_otp.html', {'error': 'Email không tồn tại.'})

    return render(request, 'send_otp.html')


def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_code = request.POST.get('otp_code')
        try:
            user = User.objects.get(email=email)
            otp = PasswordResetOTP.objects.get(user=user, otp_code=otp_code)

            # Kiểm tra thời gian OTP có hợp lệ hay không
            if otp.created_at + timedelta(minutes=5) > timezone.now():  # Thay đổi thời gian hợp lệ nếu cần
                return redirect('reset_password')  # Chuyển hướng đến trang đặt lại mật khẩu
            else:
                return render(request, 'verify_otp.html', {'error': 'Mã OTP đã hết hạn.'})

        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
            return render(request, 'verify_otp.html', {'error': 'Mã OTP không chính xác.'})

    return render(request, 'verify_otp.html')


from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Lấy email từ POST
        new_password = request.POST.get('new_password')  # Lấy mật khẩu mới

        # Kiểm tra xem email và mật khẩu mới có hợp lệ không
        if email is None or new_password is None:
            messages.error(request, 'Please enter both email and new password.')
            return redirect('reset-password')

        email = email.strip()  # Xóa khoảng trắng
        try:
            user = User.objects.get(email=email)  # Kiểm tra người dùng
            # Kiểm tra mật khẩu mới
            validate_password(new_password, user=user)  # Xác thực mật khẩu mới
            user.set_password(new_password)  # Đặt mật khẩu mới
            user.save()  # Lưu người dùng
            messages.success(request, 'Password has been reset successfully.')  # Thông báo thành công
            return redirect('sign-in')  # Chuyển hướng đến trang đăng nhập
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')  # Thông báo lỗi nếu không tìm thấy
            return redirect('reset-password')
        except ValidationError as e:
            messages.error(request, e.messages)  # Hiển thị thông báo lỗi cho người dùng
            return redirect('reset-password')

    return render(request, 'reset_password.html')

from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('sign-in') 



