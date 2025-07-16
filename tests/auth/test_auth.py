from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.cache import cache
from django.test import tag
from rest_email_auth.models import EmailConfirmation, PasswordResetToken
from rest_framework.reverse import reverse

from . import CustomOAuthTestCase

User = get_user_model()

# URL constants
login_uri = reverse("auth_login")
logout_uri = reverse("auth_logout")
register_uri = reverse("auth_register")
verify_email_uri = reverse("auth_verify-email")
resend_verification_uri = reverse("auth_resend-verification")
request_pwd_reset_uri = reverse("auth_request-password-reset")
reset_pwd_uri = reverse("auth_reset-password")
configuration = reverse("auth_configuration")


@tag("api", "user")
class TestUserAuth(CustomOAuthTestCase):
    def setUp(self):
        self.testregisteruser = {
            "email": "testregisteruser@test.com",
            "username": "testregisteruser",
            "first_name": "testregisteruser",
            "last_name": "testregisteruser",
            "password": "testregisteruser",
            "profile": {
                "company_name": "companytest",
                "company_role": "threatmatrix test",
                "twitter_handle": "@fake",
                "discover_from": "other",
            },
        }
        mail.outbox = []

    def tearDown(self):
        cache.clear()

    def test_login_200(self):
        self.assertEqual(Session.objects.count(), 0)
        response = self.client.post(login_uri, self.creds)
        self.assertEqual(response.status_code, 200)
        session_data = Session.objects.first().get_decoded()
        self.assertIn("_auth_user_id", session_data)
        self.assertEqual(str(self.user.pk), session_data["_auth_user_id"])

    def test_logout_204(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(logout_uri)
        self.assertEqual(response.status_code, 200)

    def test_register_username_taken_400(self):
        user_count = User.objects.count()
        data = {
            **self.creds,
            "first_name": "blah",
            "last_name": "blah",
            "email": self.testregisteruser["email"],
        }
        response = self.client.post(register_uri, data)
        content = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "A user with that username already exists.", content["errors"]["username"]
        )
        self.assertEqual(User.objects.count(), user_count)

    def test_register_no_email_leak_201(self):
        user_count = User.objects.count()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.testregisteruser["username"])

        self.__register_user(self.testregisteruser)
        self.assertEqual(User.objects.count(), user_count + 1)

        dup_data = {
            "email": self.testregisteruser["email"],
            "username": "blah",
            "first_name": "blah",
            "last_name": "blah",
            "password": "averystrongpassword",
            "profile": self.testregisteruser["profile"],
        }
        self.__register_user(dup_data)
        self.assertEqual(User.objects.count(), user_count + 1)

    def test_register_201(self):
        user_count = User.objects.count()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.testregisteruser["username"])

        self.__register_user(self.testregisteruser)
        user = User.objects.get(username=self.testregisteruser["username"])
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertFalse(user.is_active)
        self.assertEqual(user.profile.company_name, "companytest")
        user.delete()

    def test_verify_email_200(self):
        self.__register_user(self.testregisteruser)
        user = User.objects.get(username=self.testregisteruser["username"])
        self.assertFalse(user.is_active)

        email_obj = EmailConfirmation.objects.get(email=user.email_addresses.first())
        response = self.client.post(verify_email_uri, {"key": email_obj.key})
        response.json()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "ThreatMatrix - Please Verify Your Email Address"
        )
        self.assertEqual(mail.outbox[0].to[0], user.email)
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_resend_verification_email_200(self):
        self.__register_user(self.testregisteruser)
        response = self.client.post(
            resend_verification_uri, {"email": self.testregisteruser["email"]}
        )
        content = response.json()

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["email"], self.testregisteruser["email"])

    def test_password_reset_flow_200(self):
        self.__register_user(self.testregisteruser)
        user = User.objects.get(username=self.testregisteruser["username"])
        email_obj = user.email_addresses.first()
        email_obj.is_verified = True
        email_obj.save()

        self.client.post(request_pwd_reset_uri, {"email": user.email})
        reset_token = PasswordResetToken.objects.get(email=email_obj)
        new_password = "new_password_for_test_1234"

        response = self.client.post(
            reset_pwd_uri, {"key": reset_token.key, "password": new_password}
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_min_password_length_400(self):
        user_count = User.objects.count()
        body = {
            **self.creds,
            "email": self.testregisteruser["email"],
            "username": "blah",
            "password": "short",
        }
        response = self.client.post(register_uri, body)
        content = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid password", content["errors"]["password"])
        self.assertEqual(User.objects.count(), user_count)

    def test_special_characters_password_400(self):
        user_count = User.objects.count()
        body = {
            **self.creds,
            "email": self.testregisteruser["email"],
            "username": "blah",
            "password": "invalid$char",
        }
        response = self.client.post(register_uri, body)
        content = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid password", content["errors"]["password"])
        self.assertEqual(User.objects.count(), user_count)

    def __register_user(self, body: dict):
        response = self.client.post(register_uri, body, format="json")
        content = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content["username"], body["username"])
        self.assertEqual(content["email"], body["email"])
        self.assertFalse(content["is_active"])


class CheckConfigurationTestCase(CustomOAuthTestCase):
    def setUp(self):
        self.assertEqual(configuration, "/api/auth/configuration")

    def test_default_from(self):
        with self.settings(DEFAULT_FROM_EMAIL="", DEFAULT_EMAIL=""):
            data = self.client.get(f"{configuration}?page=register").json()
            self.assertIn("errors", data)
            self.assertIn("DEFAULT_FROM_EMAIL", data["errors"])
            self.assertIn("DEFAULT_EMAIL", data["errors"])

        with self.settings(
            DEFAULT_FROM_EMAIL="a@b.c",
            DEFAULT_EMAIL="a@b.c",
            EMAIL_HOST="x",
            EMAIL_HOST_USER="x",
            EMAIL_HOST_PASSWORD="x",
            EMAIL_PORT="x",
        ):
            for page in ["register", "login"]:
                data = self.client.get(f"{configuration}?page={page}").json()
                self.assertNotIn("errors", data)

    def test_smtp_setup(self):
        with self.settings(
            DEFAULT_FROM_EMAIL="a@b.c",
            DEFAULT_EMAIL="a@b.c",
            EMAIL_HOST="x",
            EMAIL_HOST_USER="x",
            EMAIL_HOST_PASSWORD="x",
            EMAIL_PORT="x",
        ):
            data = self.client.get(f"{configuration}?page=register").json()
            self.assertNotIn("errors", data)

        with self.settings(
            DEFAULT_FROM_EMAIL="a@b.c",
            DEFAULT_EMAIL="a@b.c",
            EMAIL_HOST="",
            EMAIL_HOST_USER="",
            EMAIL_HOST_PASSWORD="",
            EMAIL_PORT="",
        ):
            data = self.client.get(f"{configuration}?page=register").json()
            self.assertIn("errors", data)
            self.assertIn("SMTP backend", data["errors"])

    def test_ses_setup(self):
        with self.settings(
            DEFAULT_FROM_EMAIL="a@b.c",
            DEFAULT_EMAIL="a@b.c",
            AWS_SES="true",
            AWS_ACCESS_KEY_ID="x",
            AWS_SECRET_ACCESS_KEY="x",
        ):
            data = self.client.get(f"{configuration}?page=register").json()
            self.assertNotIn("errors", data)

        with self.settings(
            DEFAULT_FROM_EMAIL="a@b.c",
            DEFAULT_EMAIL="a@b.c",
            AWS_SES="true",
            AWS_ACCESS_KEY_ID="",
            AWS_SECRET_ACCESS_KEY="",
        ):
            data = self.client.get(f"{configuration}?page=register").json()
            self.assertIn("errors", data)
            self.assertIn("AWS SES backend", data["errors"])
