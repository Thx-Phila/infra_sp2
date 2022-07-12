from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TitleViewSet,
    CategoryViewSet,
    GenreeViewSet,
    CommentViewSet,
    ReviewViewSet,
    UserAuthView,
    MyTokenObtainView,
    UserViewSet
)

app_name = 'api'

auth = [
    path('auth/signup/', UserAuthView.as_view()),
    path('auth/token/', MyTokenObtainView.as_view())
]

router = DefaultRouter()
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreeViewSet, basename='genres')
router.register(r'users', UserViewSet, basename='users')

router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

router.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(auth)),
]
