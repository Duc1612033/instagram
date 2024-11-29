from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentForm  # Form để chỉnh sửa bình luận
import json
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Comment, Reply
from .forms import ReplyForm
from .models import Like, Comment
from .forms import NewCommentForm
from .models import Comment, Post

@login_required
def like_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        is_liked = data.get('is_liked')

        try:
            comment = Comment.objects.get(id=comment_id)

            if is_liked:
                # Nếu đã like, thì sẽ unlike
                comment.likes.remove(request.user)
                is_liked = False
            else:
                # Nếu chưa like, thì sẽ like
                comment.likes.add(request.user)
                is_liked = True

            # Lấy số lượng like sau khi thay đổi
            like_count = comment.like_count

            return JsonResponse({
                'success': True,
                'like_count': like_count,
                'is_liked': is_liked
            })

        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Comment not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
# Xóa câu trả lời
@login_required
def delete_reply(request, reply_id):
    if request.method == 'POST':
        try:
            # Lấy đối tượng reply hoặc trả về lỗi nếu không tồn tại
            reply = Reply.objects.get(id=reply_id)
            
            # Kiểm tra nếu người dùng là chủ câu trả lời hoặc chủ bài viết
            if reply.user == request.user or reply.comment.post.user == request.user:
                reply.delete()
                return HttpResponse(status=204)  # Trả về HTTP 204 No Content
            else:
                return JsonResponse({'error': 'Bạn không có quyền xóa câu trả lời này.'}, status=403)
        
        except Reply.DoesNotExist:
            return JsonResponse({'error': 'Câu trả lời không tồn tại.'}, status=404)
    
    return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)


def edit_reply(request, reply_id):
    try:
        # Kiểm tra tồn tại của Reply
        reply = get_object_or_404(Reply, id=reply_id)

        if request.method == "POST":
            if reply.user != request.user:
                return JsonResponse({"error": "Bạn không có quyền sửa câu trả lời này."}, status=403)

            # Lấy nội dung từ request
            data = json.loads(request.body)
            reply_body = data.get('body')

            if not reply_body:
                return JsonResponse({"error": "Nội dung không được để trống."}, status=400)

            # Cập nhật nội dung Reply
            reply.body = reply_body
            reply.save()
            return JsonResponse({"message": "Câu trả lời đã được cập nhật."}, status=200)
        else:
            return JsonResponse({"error": "Chỉ chấp nhận phương thức POST."}, status=405)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Dữ liệu không hợp lệ."}, status=400)
    except Reply.DoesNotExist:
        # Trường hợp Reply không tồn tại
        return JsonResponse({"error": "Reply không tồn tại."}, status=404)
    except Exception as e:
        # Xử lý lỗi không mong muốn
        return JsonResponse({"error": f"Lỗi hệ thống: {str(e)}"}, status=500)



def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        form = NewCommentForm(request.POST, request.FILES)  # Nhận cả FILES
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post-details', post_id=post.id)
    else:
        form = NewCommentForm()
    return render(request, 'add_comment.html', {'form': form})

def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.comment = parent_comment
            reply.save()
            return redirect("post-details", post_id=str(parent_comment.post.id))
    else:
        form = ReplyForm()

    return render(request, "reply_comment.html", {"form": form, "parent_comment": parent_comment})

# Sửa bình luận
@csrf_exempt  # Tạm thời loại bỏ CSRF để dễ dàng thử nghiệm, hãy bảo mật sau khi chạy
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Kiểm tra quyền của người dùng
    if comment.user != request.user:
        return JsonResponse({"error": "Bạn không có quyền sửa bình luận này."}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            comment_body = data.get('body')

            if comment_body:
                comment.body = comment_body
                comment.save()
                return JsonResponse({"message": "Bình luận đã được cập nhật."}, status=200)
            else:
                return JsonResponse({"error": "Không có dữ liệu body."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Dữ liệu không hợp lệ."}, status=400)
    else:
        return JsonResponse({"error": "Yêu cầu không hợp lệ."}, status=400)
@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        # Lấy bình luận hoặc trả về 404 nếu không tìm thấy
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Kiểm tra quyền: người dùng phải là chủ bình luận hoặc chủ bài viết
        if comment.user == request.user or comment.post.user == request.user:
            # Xóa bình luận
            comment.delete()
            return redirect('post-details', post_id=comment.post.id)  # Redirect về trang chi tiết bài viết
        else:
            return JsonResponse({'error': 'Bạn không có quyền xóa bình luận này.'}, status=403)
    
    return JsonResponse({'error': 'Yêu cầu không hợp lệ.'}, status=400)

