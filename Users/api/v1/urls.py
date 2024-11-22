# urls.py
from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,StudentListAPIView,SupervisorListAPIView,GroupCreateView,
    RequestedGroupsAPIView,AcceptGroupAPIView,RejectGroupAPIView,UserInfoAPIView,
    UploadCommentView, UploadFileView,GroupRetrieveAPIView, UpdateStudentMarkView,
    NoticeListAPIView, StatusUpdateAPIView
)
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('token/', obtain_auth_token, name='token_obtain_pair'),
    path('notices/', NoticeListAPIView.as_view(), name='notice_list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('students/',StudentListAPIView.as_view(), name='students'),
    path('supervisors/',SupervisorListAPIView.as_view(), name='supervisors'),
    path('groups/<int:pk>/', GroupRetrieveAPIView.as_view(), name='group-detail'),
    path('groups/create/', GroupCreateView.as_view(), name='group-create'),
     path('groups/requested/', RequestedGroupsAPIView.as_view(), name='requested-groups'),
    path('groups/<int:group_id>/accept/', AcceptGroupAPIView.as_view(), name='accept-group'),
    path('groups/<int:pk>/update-status/', StatusUpdateAPIView.as_view(), name='status-update'),
    path('groups/<int:group_id>/reject/', RejectGroupAPIView.as_view(), name='reject-group'),
    path('user-info/', UserInfoAPIView.as_view(), name='user-info'),
    path('groups/<int:group_id>/upload-comment/', UploadCommentView.as_view(), name='upload-comment'),
    path('groups/<int:group_id>/upload-files/', UploadFileView.as_view(), name='upload-file'),
    path('students/<int:pk>/update-marks/', UpdateStudentMarkView.as_view(), name='update-student-marks'),
]
