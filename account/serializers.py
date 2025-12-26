from rest_framework.serializers import ModelSerializer, ValidationError, CharField
from .models import CustomUser
from .enums import RoleChoices

class UserSerializer(ModelSerializer):
    password = CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email','password','role']

    def validate_role(self, value):
        request= self.context.get("request")
        if not request or not request.user.is_authenticated:
            return value
        
        current_user = request.user
        if current_user.role == RoleChoices.MANAGER and value != RoleChoices.DEVELOPER:
            raise ValidationError("Manager can assign only Developer role.")
        if current_user.role == RoleChoices.DEVELOPER:
            raise ValidationError("You are not allowed to change roles.")
        return value
    
    def create(self, validated_data):
        request = self.context['request']
        if request and request.user.is_authenticated:
            if request.user.role == RoleChoices.MANAGER:
                validated_data['role'] = RoleChoices.DEVELOPER
        return CustomUser.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class AdminSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email','role']
        read_only_fields = ['id', 'email']
        
    def validate_role(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == RoleChoices.MANAGER and value != RoleChoices.DEVELOPER:
                raise ValidationError("Manager can create only Developers")
        return value
    
    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance