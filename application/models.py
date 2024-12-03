from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission
from .patterns.observer import Subject
import datetime


# Validation functions
def validate_TIN(value):
    value = str(value)
    if not value.isdigit():
        raise ValidationError("TIN must be 9 digits.")
    if len(value) != 9:
        raise ValidationError("TIN must be 9 digits.")

def validate_tax_year(value):
    current_year = datetime.datetime.now().year
    if value < 2000 or value >current_year:
        raise ValidationError("Invalid year.")
    

# Concrete Subject "Client"
class Client(models.Model, Subject):
    # Dictionary of filing type options
    FILING_TYPE_DEFAULT = ''
    FILING_TYPE_SIMPLE = 'Simple'
    FILING_TYPE_CREDITS = 'Credits'
    FILING_TYPE_ITEMIZING = 'Itemizing'
    FILING_TYPE_SOLE_PROP = 'Sole Proprietor'
    FILING_TYPE_CORPORATION = 'Corporation'
    FILING_TYPE_CHOICES = {
        FILING_TYPE_DEFAULT: '',
        FILING_TYPE_SIMPLE: 'Simple',
        FILING_TYPE_CREDITS: 'Credits',
        FILING_TYPE_ITEMIZING: 'Itemizing',
        FILING_TYPE_SOLE_PROP: 'Sole Proprietor',
        FILING_TYPE_CORPORATION: 'Corporation'
        }
    
    # Dictionary of product type options
    PRODUCT_TYPE_DEFAULT = ''
    PRODUCT_TYPE_PERSONAL = 'Personal Taxes'
    PRODUCT_TYPE_CORPORATE = 'Corporate Taxes'
    PRODUCT_TYPE_EXTENSION = 'Extension'
    PRODUCT_TYPE_AMENDMENT = 'Amendment'
    PRODUCT_TYPE_WITHHOLDINGS = 'Withholdings Adjustment'
    PRODUCT_TYPE_ADVISORY = 'Advisory'
    PRODUCT_TYPE_REJECT_CORRECTION = 'Reject Correction'
    PRODUCT_TYPE_CHOICES = {
        PRODUCT_TYPE_DEFAULT: '',
        PRODUCT_TYPE_PERSONAL: 'Personal Taxes',
        PRODUCT_TYPE_CORPORATE: 'Corporate Taxes',
        PRODUCT_TYPE_EXTENSION: 'Extension',
        PRODUCT_TYPE_AMENDMENT: 'Amendment',
        PRODUCT_TYPE_WITHHOLDINGS: 'Withholdings Adjustment',
        PRODUCT_TYPE_ADVISORY: 'Advisory',
        PRODUCT_TYPE_REJECT_CORRECTION: 'Reject Correction'
    }
    
    # Client Attributes
    TIN = models.CharField(max_length = 9, validators = [validate_TIN], null = True, blank = True)
    name = models.CharField(max_length = 50, default = "", null = True, blank = True)
    email = models.EmailField(max_length = 150, null = True, blank = True)
    filing_type = models.CharField(max_length = 100, choices = FILING_TYPE_CHOICES,default = FILING_TYPE_DEFAULT, null = True, blank = True)
    tax_year = models.SmallIntegerField(validators = [validate_tax_year], default = datetime.datetime.now().year, null = True, blank = True)
    product = models.CharField(max_length = 100, choices = PRODUCT_TYPE_CHOICES, default = PRODUCT_TYPE_DEFAULT, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True, null = True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observers = []

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, **kwargs):
        for observer in self._observers:
            observer.update(**kwargs)    

    def __str__(self):
        return(f"{self.TIN} {self.name} {self.filing_type} {self.tax_year} {self.product}")


# Contributing users within an organization
class OrgUser(AbstractUser):
    # Dictionary of User Options
    USER_ROLES = (
        ('Admin', 'Administrator'),
        ('Staff', 'Staff')
    )
    role = models.CharField(max_length = 25, choices = USER_ROLES)

    #NOTE: Code used from Chatgpt to resolve discrepencies with reverse accessor for User class
    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name = "orguser_groups", # This is a custom name
        blank = True,
        help_text = "The groups this user belongs to.",
        verbose_name = "groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name = "orguser_permissions", # This is a custom name
        blank = True,
        help_text = "Specific permissions for this user.",
        verbose_name = "user permissions"
    )