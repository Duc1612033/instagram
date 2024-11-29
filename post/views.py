from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect

from post.models import Post, Tag, Follow, Stream, Likes
from django.contrib.auth.models import User
from post.forms import NewPostform,PostForm
from authy.models import Profile
from django.urls import resolve
from comment.models import Comment
from comment.forms import NewCommentForm
from django.core.paginator import Paginator

from django.db.models import Q
# from post.models import Post, Follow, Stream

from group.views import Group,GroupForm
from django.contrib import messages
from django.urls import reverse
from .forms import PostPrivacyForm
from friends.models import Friend

from page.models import Page
from django.db.models import Q



from django.http import JsonResponse
from .models import Post, Reaction
from django.db.models import Count

@login_required
def PostDetail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)

    # Kiểm tra quyền riêng tư
    if post.privacy == 'only_me' and post.user != request.user:
        return redirect('index')
    elif post.privacy == 'friends' and not (post.user == request.user or Friend.objects.filter(user=request.user, friend=post.user).exists()):
        return redirect('index')

    # Tính tổng số lượt react
    total_reactions = post.reactions.count()

    # Lấy danh sách bình luận
    comments = Comment.objects.filter(post=post).order_by('-date')

    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post-details', args=[post.id]))
    else:
        form = NewCommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'total_reactions': total_reactions,
    }

    return render(request, 'postdetail.html', context)


@login_required
def react_to_post(request, post_id, emoji):
    user = request.user
    post = get_object_or_404(Post, id=post_id)

    # Tạo hoặc cập nhật reaction
    reaction, created = Reaction.objects.get_or_create(user=user, post=post, defaults={'emoji': emoji})
    if not created:
        if reaction.emoji != emoji:
            reaction.emoji = emoji
            reaction.save()
        else:
            reaction.delete()

    # Tính lại tổng số reactions
    total_reactions = post.reactions.count()
    return JsonResponse({'total_reactions': total_reactions})





def search_posts(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(caption__icontains=query) | 
            Q(tags__name__icontains=query)  # Tìm kiếm theo thẻ
        ).distinct()
    else:
        posts = []
    return render(request, 'search_results.html', {'posts': posts, 'query': query})



@login_required
def update_privacy(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.user:
        return redirect('index')  # Hoặc trang phù hợp khác

    if request.method == 'POST':
        form = PostPrivacyForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post-details', post_id=post.id)
    else:
        form = PostPrivacyForm(instance=post)

    return render(request, 'update_privacy.html', {'form': form, 'post': post})








def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Bài viết đã được cập nhật.")
            return redirect(reverse("post-details", args=[post.id]))
    else:
        form = PostForm(instance=post)
    return render(request, "update_post.html", {"form": form, "post": post})

@login_required
def delete_post(request, post_id):
    # Lấy bài viết từ ID, nếu không có sẽ trả về lỗi 404
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        # Xóa bài viết
        post.delete()
        messages.success(request, "Bài viết đã được xóa.")

        # Lấy thông tin từ request.GET hoặc request.POST (cả GET và POST đều có thể chứa thông tin này)
        app_name = request.GET.get('app_name') or request.POST.get('app_name')
        page_name = request.GET.get('page_name') or request.POST.get('page_name')
        group_id = request.GET.get('group_id') or request.POST.get('group_id')
        username = request.GET.get('username') or request.POST.get('username')

        # Điều hướng dựa trên app_name, page_name, và các tham số khác
        if app_name == 'profile' and username:
            return redirect('profile', username=username)

        elif app_name == 'group' and page_name == 'group_detail' and group_id:
            return redirect('group_detail', group_id=group_id)

        # Nếu không xác định rõ, điều hướng về trang index
        return redirect('index')  # Hoặc trang chủ nếu không xác định rõ

    # Nếu không phải POST, điều hướng lại trang chi tiết bài viết
    return redirect('post-details', post_id=post_id)






@login_required
def index(request):
    user = request.user
    all_users = User.objects.all()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    profile = Profile.objects.all()

    # Lấy tất cả các bài viết từ Stream của người dùng
    posts = Stream.objects.filter(user=user)
    group_ids = [post.post_id for post in posts]
    
    # Lọc các bài viết có id trong group_ids và sắp xếp theo thứ tự mới nhất
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    

    # Áp dụng lọc quyền riêng tư cho các bài viết
    # Áp dụng lọc quyền riêng tư cho các bài viết
    filtered_posts = []
    for post in post_items:
    # Kiểm tra quyền riêng tư cho từng bài viết
        if post.privacy == 'only_me' and post.user == request.user:
            filtered_posts.append(post)
        elif post.privacy == 'friends' and (
            post.user == request.user or Friend.objects.filter(user=request.user, friend=post.user).exists()
        ):
            filtered_posts.append(post)
        elif post.privacy == 'public':
            filtered_posts.append(post)


    # Tìm kiếm người dùng nếu có truy vấn
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

    # Truyền danh sách bài viết đã được lọc vào context
    context = {
        'post_items': filtered_posts,  # Sử dụng danh sách đã lọc
        'follow_status': follow_status,
        'profile': profile,
        'all_users': all_users,
        # 'users_paginator': users_paginator,  # Bỏ ghi chú nếu muốn dùng phần tìm kiếm người dùng
    }
    return render(request, 'index.html', context)




@login_required
def NewPost(request, app_name=None, page_name=None):
    print("app_name:", app_name)  # In ra giá trị của app_name
    print("page_name:", page_name)  # In ra giá trị của page_name
    user = request.user
    tags_obj = []
    group = None
    page = None  # Đặt `page` là None để chỉ lấy khi cần

     # Kiểm tra `app_name` và xử lý theo từng trường hợp
    if app_name == 'group' and page_name == 'group_detail':
        # Nếu là trang nhóm, lấy `Group` theo `group_id`
        group_id = request.POST.get('group_id') or request.GET.get('group_id')
        if group_id:
            group = get_object_or_404(Group, id=group_id)
    elif app_name == 'profile':
        # Nếu là trang cá nhân `profile`, không cần lấy `Page`
        page = None
    else:
        # Trường hợp khác, kiểm tra `Page`
        try:
            page = Page.objects.get(title=page_name)
        except Page.DoesNotExist:
            return redirect('index')  # Điều hướng nếu không tìm thấy `Page`

    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tag_form = form.cleaned_data.get('tags')
            tag_list = list(tag_form.split(','))

            for tag in tag_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_obj.append(t)
                
            # Tạo Post có thể có `group` hoặc `page`
            p = Post.objects.create(
                picture=picture,
                caption=caption,
                user=user,
                group=group
            )
            p.tags.set(tags_obj)
            p.save()

            # Điều hướng tùy thuộc vào `app_name` và `page_name`
            if app_name == 'group' and page_name == 'group_detail' and group:
                return redirect('group_detail', group_id=group.id)
            elif app_name == 'profile':
                return redirect('profile', username=user.username)
            return redirect('index')
    else:
        form = NewPostform()
        
    context = {'form': form, 'app_name': app_name, 'page_name': page_name}
    return render(request, 'newpost.html', context)






@login_required
def Tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    context = {
        'posts': posts,
        'tag': tag

    }
    return render(request, 'tag.html', context)


# Like function
@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        Likes.objects.create(user=user, post=post)
        current_likes = current_likes + 1
    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1
        
    post.likes = current_likes
    post.save()
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))

@login_required
def favourite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))






