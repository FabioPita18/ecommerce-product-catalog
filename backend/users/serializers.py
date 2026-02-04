"""
User Serializers for Django REST Framework.

This module will contain serializers for:
- User registration
- User profile (read/update)
- Password change

Key Considerations:
- Never expose password field in responses
- Use write_only=True for password in create/update serializers
- Validate password strength during registration
- Use Django's password hashers (never store plain text)

Serializers to implement (Phase 4):
- UserSerializer: For reading user profile
- UserCreateSerializer: For registration (includes password validation)
- UserUpdateSerializer: For profile updates (no password)
- PasswordChangeSerializer: For changing password

Example:
    class UserCreateSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, min_length=8)
        password_confirm = serializers.CharField(write_only=True)

        class Meta:
            model = User
            fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']

        def validate(self, attrs):
            if attrs['password'] != attrs.pop('password_confirm'):
                raise serializers.ValidationError("Passwords do not match")
            return attrs

        def create(self, validated_data):
            return User.objects.create_user(**validated_data)
"""
