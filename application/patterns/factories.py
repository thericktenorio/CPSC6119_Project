from application.models import OrgUser


class UserFactory:
    @staticmethod
    def create_user(role, **kwargs):
        if role == 'Admin':
            return AdminFactory.create_user(**kwargs)
        elif role == 'Staff':
            return StaffFactory.create_user(**kwargs)
        else:
            raise ValueError("Invalid user type.")

class AdminFactory(UserFactory):
    @staticmethod
    def create_user(**kwargs):
        user = OrgUser(**kwargs)
        user.role = 'Admin'
        user.is_staff = True
        user.is_superuser = False
        user.save()
        return user


class StaffFactory(UserFactory):
    @staticmethod
    def create_user(**kwargs):
        user = OrgUser(**kwargs)
        user.role = "Staff"
        user.is_staff = True
        user.is_superuser = False
        user.save()
        return user