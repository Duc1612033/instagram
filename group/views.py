import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Group, Membership
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from post.models import Post 
from .forms import GroupForm  # Giả sử bạn đã tạo form cho Group
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import JsonResponse

from django.db.models import Q


def search_groups(request):
    query = request.GET.get('q', '')
    groups = Group.objects.filter(name__icontains=query) if query else []
    return render(request, 'group/search_results.html', {'groups': groups, 'query': query})

@require_POST
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect(reverse('list_groups')) 

@require_POST
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.name = request.POST.get('name')
    group.description = request.POST.get('description')
    group.save()
    return redirect(reverse('group_detail', args=[group_id]))    
# Hiển thị danh sách tất cả các nhóm
@login_required
def list_groups(request):
    groups = Group.objects.all()
    return render(request, 'group/group_list.html', {'groups': groups})

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Thêm logic tham gia nhóm, ví dụ:
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)
    membership.is_approved = False  # Có thể là yêu cầu cần được duyệt
    membership.save()
    return redirect("list_groups")

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            messages.success(request, "Group created successfully!")
            return redirect("list_groups")  # Điều hướng về danh sách nhóm sau khi tạo
    else:
        form = GroupForm()

    return render(request, "group/create_group.html", {"form": form})


@login_required
def toggle_post_permission(request, group_id, member_id):
    group = get_object_or_404(Group, id=group_id)
    member = get_object_or_404(Membership, id=member_id, group=group)

    if request.user == group.admin:  # Chỉ admin mới có quyền thay đổi
        # Đảo ngược giá trị của can_post
        member.can_post = not member.can_post
        member.save()

    return redirect(reverse('view_group_members', args=[group.id]))



def toggle_membership(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Kiểm tra nếu người dùng đã là thành viên của nhóm
    if request.user in group.members.all():
        # Nếu là thành viên, xóa họ khỏi nhóm (hủy tham gia)
        group.members.remove(request.user)
        action = 'left'
    else:
        # Nếu không phải thành viên, thêm họ vào nhóm (tham gia)
        group.members.add(request.user)
        action = 'joined'
    
    # Nếu bạn muốn trả về JSON và vẫn chuyển hướng, bạn có thể làm như sau:
    # Trả về phản hồi JSON với trạng thái
    response_data = {'status': 'success', 'action': action}
    
    # Chuyển hướng về group_list
    return redirect(reverse('list_groups')) 


@login_required
def view_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = Membership.objects.filter(group=group, is_approved=True)

    return render(request, 'group/view_members.html', {
        'group': group,
        'members': members,
    })
# Hiển thị trang chi tiết nhóm với các bài viết ngẫu nhiên


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
     # Kiểm tra nếu người dùng là thành viên và có quyền đăng bài
    can_post = Membership.objects.filter(group=group, user=request.user, can_post=True).exists()
    # Lấy tất cả bài viết liên kết với nhóm này
    group_posts = Post.objects.filter(group=group)
    
    return render(request, 'group/group_detail.html', {
        'group': group,
        'can_post': can_post,
        'random_posts': group_posts,  # Hiển thị bài viết của nhóm
    })
# Gửi yêu cầu tham gia nhóm
@login_required
def join_group_request(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)
    if created:
        messages.success(request, "Yêu cầu tham gia đã được gửi!")
    else:
        messages.warning(request, "Bạn đã gửi yêu cầu hoặc là thành viên của nhóm này!")
    return redirect('group_detail', group_id=group_id)

# Quản lý yêu cầu tham gia nhóm của admin
@login_required
def manage_requests(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user != group.admin:
        messages.error(request, "Bạn không phải admin của nhóm này!")
        return redirect('list_groups')
    
    requests = Membership.objects.filter(group=group, is_approved=False)
    return render(request, 'group/manage_requests.html', {'group': group, 'requests': requests})

# Chấp nhận hoặc từ chối yêu cầu
@login_required
def approve_request(request, membership_id, action):
    membership = get_object_or_404(Membership, id=membership_id)
    if request.user != membership.group.admin:
        messages.error(request, "Bạn không có quyền thực hiện thao tác này!")
        return redirect('manage_requests', group_id=membership.group.id)

    if action == 'approve':
        membership.is_approved = True
        membership.save()
        messages.success(request, f"Đã chấp nhận yêu cầu từ {membership.user.username}.")
    elif action == 'deny':
        membership.delete()
        messages.success(request, f"Đã từ chối yêu cầu từ {membership.user.username}.")
    
    return redirect('manage_requests', group_id=membership.group.id)


def remove_member(request, group_id, member_id):
    # Kiểm tra nếu người dùng có quyền xóa thành viên
    membership = get_object_or_404(Membership, id=member_id, group_id=group_id)
    membership.delete()
    return redirect('view_members', group_id=group_id)
