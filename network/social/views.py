from datetime import datetime
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from django.shortcuts import get_object_or_404
from django.db.models import Count, DateField
from django.db.models import F 

from .serializers import (LoginSerializer, RegistrationSerializer, UserSerializer, PostSerializer, 
                            LikeSerializer, AnalyticsSerializer, ActivitySerializer)

from .renderers import UserJSONRenderer
from .models import Post, Like, User

class RegistrationAPIView(APIView):
   
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):

    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        #Authentication happpens in validate method of serializer
        
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
       
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)
    
    def create(self, request, post_id, *args, **kwargs):
        
        try:
            post = Post.objects.get(id=post_id)

        except:
            return Response({"errors":{"error": f"Couldn't find post with this id: {post_id}"}}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {"post": post.pk}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=self.request.user)

        post.likes_count+=1
        post.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, post_id, *args, **kwargs):

        user = request.user

        like = get_object_or_404(Like, post=post_id, user=user)
        like.delete()

        post = Post.objects.get(id=post_id)
        post.likes_count-=1
        post.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT) 


class AnalyticsViewSet(viewsets.ViewSet):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = AnalyticsSerializer
    
    def list(self, request):

        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from is None or date_to is None:
            return Response({"errors":{"error": "date_from and date_to parameters are required."}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            return Response({"errors":{"error": "date_from and date_to must be in format YYYY-MM-DD."}}, status=status.HTTP_400_BAD_REQUEST)

        analytics = (
            Like.objects
            .filter(created_at__gte=date_from, created_at__lte=date_to)
            .values('post')
            .annotate(created_date = F('created_at__date'), likes_count=Count('id'))
        )
    
        serializer = AnalyticsSerializer(analytics, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserActivity(ListAPIView):

    permission_classes = (IsAuthenticated,)

    def list(self, request, user_id):
        
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({"errors":{"error": f"Couldn't find user with this id: {user_id}"}}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ActivitySerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
        