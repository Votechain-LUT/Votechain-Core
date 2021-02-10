""" Module defining serializers for models """
from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers
from core.models.models import Candidate, Poll, Voter


User = get_user_model()
password_style = {"input_type": "password", "placeholder": "Password"}


class CandidateNestedSerializer(serializers.ModelSerializer):
    """ Serializer for nested candidate model """
    class Meta:
        model = Candidate
        fields = ("id", "name")
        depth = 1


class PollSerializer(serializers.ModelSerializer):
    """ Serializer for poll model """
    candidates = CandidateNestedSerializer(many=True, read_only=True)
    class Meta:
        model = Poll
        fields = "__all__"
        depth = 1

    def validate(self, attrs):
        """
        Check that poll starts before it ends.
        """
        if attrs['start'] > attrs['end']:
            raise serializers.ValidationError("End date must be later than start date")
        return attrs


class CandidateSerializer(serializers.ModelSerializer):
    """ Serializer for standalone candidate model """
    poll = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Poll.objects.all()
        )

    class Meta:
        model = Candidate
        fields = "__all__"
        depth = 1


class VoterSerializer(serializers.ModelSerializer):
    """ Serializer for voter model """
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email"
    )
    class Meta:
        model = Voter
        fields = "__all__"

    def update(self, instance, validated_data):
        return Voter.objects.update(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ( "id", "username", "password", "email" )


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, style=password_style)
    confirm_password = serializers.CharField(write_only=True, required=True, style=password_style)
    old_password = serializers.CharField(write_only=True, required=True, style=password_style)

    def validate_old_password(self, value):
        """ Checks if the provided old password is the same as current's user password """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                ("Provided old password doesn't match")
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("passwords must match")
        password_validation.validate_password(attrs["password"], self.context["request"].user)
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def save(self, **kwargs):
        password = self.validated_data["password"]
        user = self.context["request"].user
        voter = Voter.objects.filter(user=user).first()
        if voter is not None:
            voter.password_changed = True
            voter.save()
        user.set_password(password)
        user.save()
        return user


class VitGeneratorSerializer(serializers.Serializer):
    users = serializers.ListField(
        default=[],
        child=serializers.EmailField()
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CompleteUserSerializer(serializers.Serializer):
    user = UserSerializer()
    voter = VoterSerializer()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
