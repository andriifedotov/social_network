from django.urls import path, include

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView
from rest_framework import routers
from .views import PostViewSet, LikeViewSet

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)

post_like_list = LikeViewSet.as_view({
    'post': 'create',
    'delete': 'destroy',
    'get': 'list'
})

urlpatterns = [
    path('users/signup/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('', include(router.urls)),
    path('posts/<int:post_id>/likes/', post_like_list),
]