from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from django.shortcuts import get_object_or_404

from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer, PostSerializer, LikeSerializer
from .renderers import UserJSONRenderer
from .models import Post, Like

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
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, post_id, serializer):
            serializer.save(user=self.request.user, post=post_id)
    
    def create(self, request, post_id, *args, **kwargs):
        
        post = Post.objects.get(id=post_id)
        
        user = request.user
        data = {"user": user,"post": post_id}

        serializer = self.serializer_class(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        post.likes_count+=1
        post.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, post_id, *args, **kwargs):

        like = get_object_or_404(Like, post=post_id)
        like.delete()

        post = Post.objects.get(id=post_id)
        post.likes_count-=1
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT) 



        