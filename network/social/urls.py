from django.urls import path, include

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, AnalyticsViewSet, UserActivity
from rest_framework import routers
from .views import PostViewSet, LikeViewSet

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

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
    path('users/<int:user_id>/activity/', UserActivity.as_view())
]