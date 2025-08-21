
class FakeAdminUser:
    """
    Fake duck-typed AbstractUser for the Graphql Admin, authenticated by x-hasura-admin-secret.
    Internal services like the collab editing server will authenticate that way.
    """
    is_authenticated = True
    is_anonymous = False
    is_active = True
    is_privileged = True
    is_staff = True
    username = "[GRAPHQL ADMIN]"
    def get_username(self):
        return self.username
ADMIN_USER = FakeAdminUser()
