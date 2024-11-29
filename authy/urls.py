from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from authy.views import follow_list,upload_cover_photo,logout_view,UserProfile, EditProfile,CustomPasswordChangeView,delete_account,send_otp, verify_otp, reset_password


urlpatterns = [
   path('upload_cover_photo/', views.upload_cover_photo, name='upload_cover_photo'),
   path('toggle-privacy/', views.TogglePrivacy, name='toggle_privacy'),
    # Profile Section
    path('profile/edit', EditProfile, name="editprofile"),

    # User Authentication
    path('sign-up/', views.register, name="sign-up"),
    path('sign-in/', auth_views.LoginView.as_view(template_name="sign-in.html", redirect_authenticated_user=True), name='sign-in'),
  
#đây là urls chang password
      path('change-password/', CustomPasswordChangeView.as_view(), name='change-password'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    ##############################################################################################

    #urls quên mật khẩu
     # Đường dẫn cho việc yêu cầu đặt lại mật khẩu
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    
    # Đường dẫn cho việc gửi email đặt lại mật khẩu
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # Đường dẫn để đặt lại mật khẩu qua email
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Đường dẫn cho thông báo hoàn thành đặt lại mật khẩu
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
 path('delete_account/', delete_account, name='delete_account'),
 ##################################################
  path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('logout/', logout_view, name='sign-out'),
      path('users/reset-password/', reset_password, name='reset-password'),
    path('profile/<str:username>/', UserProfile, name='profile'),
    path('<username>/follow/<option>/', follow_list, name='follow_list'),
    
]
