# page/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .forms import PageForm
from .models import Page,Post, PageMembership
from post.models import Post
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q



def search_pages(request):
    query = request.GET.get('q', '')
    if query:
        pages = Page.objects.filter(title__icontains=query)  # Tìm kiếm theo tên trang
    else:
        pages = []
    return render(request, 'page/search_results.html', {'pages': pages, 'query': query})

@login_required
def toggle_post_permission(request, page_id, member_id):
    page = get_object_or_404(Page, id=page_id)  # Lấy trang theo ID
    
    if request.user != page.admin:
        raise Http404("Bạn không có quyền thực hiện thao tác này.")

    membership = get_object_or_404(PageMembership, id=member_id, page=page)  # Lấy thành viên của trang theo ID

    if request.user == page.admin:  # Chỉ admin của trang mới có quyền thay đổi
        # Đảo ngược giá trị của can_post
        membership.can_post = not membership.can_post
        membership.save()

    return redirect(reverse('view_members', args=[page.id]))








@login_required
def view_members(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    members = PageMembership.objects.filter(page=page, is_approved=True)  # Sử dụng PageMembership

    return render(request, 'page/view_members.html', {  # Thay 'group' thành 'page'
        'page': page,
        'members': members,
    })

@login_required
def toggle_page_membership(request, page_id):
    # Lấy đối tượng Page theo ID
    page = get_object_or_404(Page, id=page_id)
    
    # Kiểm tra nếu người dùng đã là thành viên của trang
    membership = PageMembership.objects.filter(page=page, user=request.user).first()
    
    if membership:
        # Nếu đã là thành viên, xóa họ khỏi trang (hủy tham gia)
        membership.delete()
        action = 'left'
    else:
        # Nếu chưa tham gia, thêm họ vào trang (tham gia)
        PageMembership.objects.create(page=page, user=request.user)
        action = 'joined'
    
    # Nếu bạn muốn trả về phản hồi JSON và vẫn chuyển hướng, bạn có thể làm như sau:
    # Trả về phản hồi JSON với trạng thái
    response_data = {'status': 'success', 'action': action}
    
    # Chuyển hướng về page_list
    return redirect(reverse('page_list'))

@login_required
def page_detail(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    
    # Kiểm tra xem người dùng có phải là admin không
    is_admin = request.user == page.admin
    
    # Kiểm tra xem người dùng có quyền đăng bài không
    can_post = PageMembership.objects.filter(page=page, user=request.user, can_post=True).exists()

    # Giả định rằng Page có liên kết tới Post qua related_name 'posts'
    page_posts = page.posts.all()

    return render(request, 'page/page_detail.html', {
        'page': page,
        'can_post': can_post,
        'is_admin': is_admin,
        'posts': page_posts,
    })

@login_required
def join_page_request(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    membership, created = PageMembership.objects.get_or_create(user=request.user, page=page)
    if created:
        messages.success(request, "Yêu cầu tham gia trang đã được gửi!")
    else:
        messages.warning(request, "Bạn đã gửi yêu cầu hoặc là thành viên của trang này!")
    return redirect('page_detail', page_id=page_id)

@login_required
def manage_page_requests(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    if request.user != page.admin:
        messages.error(request, "Bạn không phải admin của trang này!")
        return redirect('page_list')
    
    requests = PageMembership.objects.filter(page=page, is_approved=False)
    return render(request, 'page/manage_requests.html', {'page': page, 'requests': requests})

@login_required
def approve_page_request(request, membership_id, action):
    membership = get_object_or_404(PageMembership, id=membership_id)
    if request.user != membership.page.admin:
        messages.error(request, "Bạn không có quyền thực hiện thao tác này!")
        return redirect('manage_page_requests', page_id=membership.page.id)

    if action == 'approve':
        membership.is_approved = True
        membership.save()
        messages.success(request, f"Đã chấp nhận yêu cầu từ {membership.user.username}.")
    elif action == 'deny':
        membership.delete()
        messages.success(request, f"Đã từ chối yêu cầu từ {membership.user.username}.")
    
    return redirect('manage_page_requests', page_id=membership.page.id)

@login_required
def remove_page_member(request, page_id, member_id):
    page = get_object_or_404(Page, id=page_id)
    if request.user != page.admin:
        messages.error(request, "Bạn không phải admin của trang này!")
        return redirect(reverse('page_detail', kwargs={'pk': page_id}))

    member = get_object_or_404(User, id=member_id)
    PageMembership.objects.filter(user=member, page=page).delete()
    messages.success(request, f"{member.username} đã bị xoá khỏi trang.")
    return redirect(reverse('page_detail', kwargs={'pk': page_id}))















@login_required
def toggle_like(request, pk):
    page = get_object_or_404(Page, pk=pk)

    # Toggle the like status
    if page.likes.filter(id=request.user.id).exists():
        page.likes.remove(request.user)  # Unlike
        liked = False
    else:
        page.likes.add(request.user)  # Like
        liked = True

    # Trả về JSON chứa thông tin về trạng thái "like" và tổng số lượt "like"
    return JsonResponse({'liked': liked, 'like_count': page.likes.count()})
def post_create(request):
    # Get page_id from either query parameters (GET) or the form (POST)
    page_id = request.GET.get('page_id') or request.POST.get('page_id')
    
    if not page_id:
        # Handle the case where page_id is not provided
        return redirect('page_list')  # Redirect or show an error page

    page = get_object_or_404(Page, pk=page_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.page = page  # Associate post with the page
            post.save()
            return redirect('page_detail', pk=page.pk)  # Redirect to page detail

    else:
        form = PostForm()

    return render(request, 'page/post_create.html', {'form': form, 'page': page})
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('page_detail', pk=post.page.pk)  # Dùng pk của page
    else:
        form = PostForm(instance=post)
    return render(request, 'page/post_form.html', {'form': form})


def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    page_id = post.page.id
    post.delete()
    return redirect('page_detail', pk=page_id)  # Dùng pk của page



def about(request):
    return render(request, 'page/about.html')

def page_list(request):
    pages = Page.objects.all()
    return render(request, 'page/page_list.html', {'pages': pages})

def page_create(request):
    # Tạo trang mới với tiêu đề mặc định và gán admin là người dùng hiện tại
    page = Page.objects.create(title="New Page", admin=request.user)
    return redirect('page_detail', pk=page.pk)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Page, Post  # Import đúng các model cần thiết
from .forms import PostForm  # Import form PostForm nếu bạn đã định nghĩa

def page_detail(request, pk):
    page = get_object_or_404(Page, pk=pk)  # Thay 'id' thành 'pk'
    is_admin = request.user == page.admin 
    try:
        membership = PageMembership.objects.get(user=request.user, page=page)
        can_post = membership.can_post
    except PageMembership.DoesNotExist:
        can_post = False  # Người dùng không phải là thành viên

    
    # Xử lý form tạo bài viết mới
    if request.method == 'POST' and 'create' in request.POST:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.page = page  # Liên kết bài viết với trang
            post.save()
            return redirect('page_detail', pk=page.pk)  # Sử dụng 'pk'

    # Lấy danh sách bài viết của trang
    posts = Post.objects.filter(page=page)  # Lọc bài viết theo trang
    form = PostForm()

    return render(request, 'page/page_detail.html', {
        'page': page,
        'posts': posts,
        'form': form,
        'is_admin': is_admin,
        'can_post': can_post,
    })

def page_update(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('page_detail', pk=page.id)

    else:
        form = PageForm(instance=page)
    return render(request, 'page/page_edit.html', {'form': form, 'page': page})

def page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        page.delete()
        return redirect('page_list')
    return render(request, 'page/page_delete_confirm.html', {'page': page})
