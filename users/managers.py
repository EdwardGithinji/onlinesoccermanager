from typing import Any, Optional

from django.contrib.auth.base_user import (BaseUserManager, AbstractBaseUser)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
                     password: Optional[str] = None, **extra_fields: Any
                     ) -> AbstractBaseUser:
        """
        Creates and saves a user with a given email and password
        """
        # validation
        if not email:
            raise ValueError('A valid e-mail address must be provided')

        email = self.normalize_email(email)

        user: AbstractBaseUser = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            **extra_fields
        )

        user.set_password(password)     # type: ignore
        user.save(using=self._db)
        return user

    def create_user(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
                     password: Optional[str] = None, **extra_fields: Any
                     ) -> AbstractBaseUser:
        """
        Creates a User.
        """
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None,
                         password: Optional[str] = None, **extra_fields: Any
                         ) -> AbstractBaseUser:
        """
        Creates a Superuser
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser flag set')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff flag set')

        return self._create_user(email, first_name, last_name, password, **extra_fields)