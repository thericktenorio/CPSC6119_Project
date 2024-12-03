# NOTE: Signals (Part of Django's native app logic) may potentionally be used 
    # in later version for optimized performance after application refactoring
    # TODO: Go to "apps.py" and uncomment session management section
    # remove corresponding files and references to generalized implementations

from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib import messages


# Session Singleton via Singals
@receiver(user_logged_in)
def logout_previous_sessions(sender, request, user, **kwargs):
    # Identify current session key
    current_session_key = request.session.session_key

    # Check if user has previous session open and logout if true
    user_sessions = Session.objects.filter(expire_date__gte = now())
    for session in user_sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
            messages.warning("Multiple sessions detected. Your previous session has been ended.")
            session.delete()