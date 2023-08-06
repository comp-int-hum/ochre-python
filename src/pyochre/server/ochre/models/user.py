import logging
from django.core.validators import RegexValidator, EmailValidator, URLValidator
from django.conf import settings
from django.urls import reverse
from django.db.models import CharField, ImageField, TextField, EmailField, URLField, ForeignKey, DateTimeField, SET_NULL, IntegerField
from django.contrib.auth.models import AbstractUser
from pyochre.server.ochre.models import OchreModel


if settings.USE_LDAP:
    import ldap


phone_validator = RegexValidator(regex=r"^\s*\+?[\d\s\-]+$")
email_validator = EmailValidator()
url_validator = URLValidator()
    

logger = logging.getLogger(__name__)


class User(AbstractUser, OchreModel):
    homepage = URLField(
        blank=True,
        validators=[url_validator]
    )
    ordering = IntegerField(default=0)    
    photo = ImageField(blank=True, upload_to="user_photos")
    title = CharField(blank=True, max_length=300)
    research_interests = TextField(blank=True, max_length=1000)
    biography = TextField(blank=True)
    username = CharField(unique=True, null=True, max_length=40)
    email = EmailField(
        unique=True,
        validators=[email_validator]
    )
    location = CharField(null=True, max_length=100)
    phone = CharField(
        null=True,
        validators=[phone_validator],
        max_length=20
    )
    created_at = DateTimeField(auto_now_add=True, editable=False)
    modified_at = DateTimeField(auto_now=True, editable=False)
    created_by = ForeignKey(
        "self",
        null=True,
        on_delete=SET_NULL,
        editable=False
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    
    def set_password(self, raw_password):
        if settings.USE_LDAP:
            ld = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            if settings.AUTH_LDAP_START_TLS == True:
                ld.set_option(
                    ldap.OPT_X_TLS_CACERTFILE,
                    settings.AUTH_LDAP_CERT_FILE
                )
                ld.set_option(
                    ldap.OPT_X_TLS_REQUIRE_CERT,
                    ldap.OPT_X_TLS_DEMAND
                )
                ld.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
                ld.start_tls_s()
                ld.simple_bind_s(
                    settings.AUTH_LDAP_BIND_DN,
                    settings.AUTH_LDAP_BIND_PASSWORD
                )
            else:
                ld.bind_s(
                    settings.AUTH_LDAP_BIND_DN,
                    settings.AUTH_LDAP_BIND_PASSWORD
                )
            dn = "uid={},{}".format(
                self.username,
                settings.LDAP_USER_BASE
            )
            ld.passwd_s(dn, None, raw_password)
        else:
            super().set_password(raw_password)

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        ) if self.last_name else self.username
