from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from .patterns.singleton import SessionManager
from .forms import SignUpForm
from .models import Client, OrgUser
import pandas as pd


# Accessing 'Home' page via login
def home(request):
    clients = Client.objects.all()
    try:    # This try block is partly used in updating the home page when a new row (ie client) is added
        latest_client = Client.objects.latest('id')
    except Client.DoesNotExist:
       latest_client = None
    # Check user loggin
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(request, username = username, password = password)
        if user is not None:
            
            # Instantiate session singleton
            session_manager = SessionManager()
            
            # End existing sessions if any
            existing_session = session_manager.get_active_session(user.pk)
            if existing_session:
                messages.info(request, f"Multisessions for user {user.pk} is prohibited. Prior session {existing_session} has been terminated.")

            # Login
            login(request, user)
            session_manager.start_session(user.pk, request.session.session_key)
            success_message = f"Login successful. User ID: {user.pk} is currently using Session ID: {session_manager.get_active_session(user.pk)}"
            messages.success(request, success_message)
            return redirect("home")
        else:
            messages.success(request, "Error logging in. Please try again.")
            return redirect("home")
    else:
        return render(request, "home.html", {'clients':clients, 'latest_client':latest_client})


# Create a new client
def create_new_client(request):
    try:
        if request.method == "POST":
            # Create new client
            new_client = Client(TIN = "", name = "", filing_type = "", product = "", email = "example@example.com")
            new_client.save()
            # Connect observers to client
            try:
                # get observer instances
                app_config = apps.get_app_config('application')
                tin_observer = app_config.tin_observer
                advisory_observer = app_config.advisory_observer
                #Connect Client to observers
                new_client.add_observer(tin_observer)
                new_client.add_observer(advisory_observer)
            except Exception as e:
                messages.error(request, "Unable to connect observers to new client.")
        return JsonResponse({'status': 'success',
                             'client_id': new_client.pk, 
                             'TIN': new_client.TIN, 
                             'name': new_client.name, 
                             'filing_type': new_client.filing_type, 
                             'tax_year': new_client.tax_year, 
                             'product': new_client.product })
    except Exception as e:
        return JsonResponse({'status':'error', 'message':str(e)}, status = 500)


# Automatically update client details
def auto_update_client(request):
    if request.method == "POST":
        client_id = request.POST.get('client_id')
        field = request.POST.get('field')
        value = request.POST.get('value')

        # Attempt to access client id
        try:
            client = Client.objects.get(id = client_id)
        except Client.DoesNotExist:
            return JsonResponse({'status': 'error', 'message':'Client not found.'}, status = 404)
        
        # Define the observer data
        observer_data = {
            'id':client.pk,
            'TIN': client.TIN,
            'name': client.name,
            'filing_type': client.filing_type,
            'tax_year': client.tax_year,
            'product': client.product,
        }

        # Update cells and notify observers
        if field == 'TIN':
            client.TIN = value
            observer_data['TIN'] = value
        elif field == 'name':
            client.name = value
            observer_data['name'] = value
        elif field == 'filing_type':
            if value in dict(Client.FILING_TYPE_CHOICES):
                client.filing_type = value
                observer_data['filing_type'] = value
            else:
                return JsonResponse({'status': 'error', 'message': f'Invalid filing type: {value}'}, status = 400)
        elif field == 'tax_year':
            client.tax_year = value
            observer_data['tax_year'] = value
        elif field == 'product':
            if value in dict(Client.PRODUCT_TYPE_CHOICES):
                client.product = value
                observer_data['product'] = value
            else:
                return JsonResponse({'status': 'error', 'message': f'Invalid product: {value}'}, status = 400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid field name'}, status = 400)
        
        #Re-validate client instance & save if valid
        try:
            client.full_clean() # executes all validators
            client.save()

            # Update observers
            client.notify_observers(**observer_data)
            return JsonResponse({'status': 'success'})
        except ValidationError as e:
            return JsonResponse({'status':'error', 'message':str(e)}, status = 400)
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status = 400)


# Delete client from database
def delete_client(request):
    client_id = request.POST.get('client_id') # get client id from data that is packaged in the request
    try:
        if request.method == "POST":
            client = Client.objects.get(id = client_id)
            client.delete()
            return JsonResponse({'status': 'success'})
    except Client.DoesNotExist:
        return JsonResponse({'status':'error', 'message':'Client not found'})


# User logout
def logout_user(request):
    user = request.user.pk
    session_manager = SessionManager()
    existing_session = session_manager.get_active_session(user)
    session_manager.end_session(user)
    logout(request)

    messages.success(request, f"User {user} has logged out. Session {existing_session} has ended.")
    return redirect("home")


# Register new user
def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            #username = form.cleaned_data['username']
            #password = form.cleaned_data['password1']
            #user = authenticate(username = username, password = password)
            #login(request, user)
            messages.success(request, "New user registered.")
            return redirect("home")
    else:
        form = SignUpForm()
        return render(request, "register.html", {'form':form})
    return render(request, 'register.html', {'form':form})


# Import Clients from Excel
def import_clients(request):
    if request.method == "POST":
        try:
            file = request.FILES.get('client_file')
            if not file:
                messages.error(request, "No file selected.")
                return redirect("home")
        except Exception as e:
            messages.error(request, f"Unable to load file: {e}")
            return redirect("home")
    try:
        # Read in the files
        if file.name.endswith(('.xls', '.xlsx', '.xlsm')):
            client_data = pd.read_excel(file)
        elif file.name.endswith(('.csv')):
            client_data = pd.read_csv(file)
        else:
            messages.error(request, "File type must be one of the following: .xls, .xlsx, .xlsm, .csv")
            return redirect("home")

        # Create new clients from imported client data
        for _, row in client_data.iterrows():
            Client.objects.update_or_create(
                TIN = row["TIN"],
                defaults = {
                    "name": row["Name"],
                    #may expand features in full version
                }
            )
        messages.success(request, "Import successful.")
    except Exception as e:
        messages.error(request, f"Unable to import file: {e}")
        return redirect("home")
    return redirect("home")

# Export Clients to Excel
def export_clients(request):
    if request.method == "GET":
        try:
            # Get all clients from database
            clients = Client.objects.all().values(
                'TIN',
                'name',
                'filing_type',
                'tax_year', 
                'product',
                'email',
            )
            # Convert QuerySet to dataframe
            df = pd.DataFrame(list(clients))

            # Create excel file in memory // technique acquired from Chatgpt
            response = HttpResponse(content_type = 'applicaiton/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename = clients.xlsx'
            with pd.ExcelWriter(response, engine = 'xlsxwriter') as writer:
                df.to_excel(writer, index = False, sheet_name = f'Clients')
            
            # Return excel to user
            return response
        except Exception as e:
            messages.error(request, f"Unable to export clients: {e}")
            return redirect("home")
    else:
        messages.error(request, "Invalid request method.")
        return redirect("home") 


# Audit Client Logs
def audit_client_logs(request):
    if request.method == "GET":
        try:
            # Access persistent observers
            app_config = apps.get_app_config('application')
            tin_observer = app_config.tin_observer
            advisory_observer = app_config.advisory_observer
            # Gather all observer notifications
            all_messages = [
                {"Observer": "TINObserver", "Message": msg} for msg in tin_observer.notifications
            ] + [
                {"Observer": "AdvisoryObserver", "Message":msg} for msg in advisory_observer.notifications
            ]
            # Convert notifications to dataframe
            df = pd.DataFrame(all_messages)
            response = HttpResponse(content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename = observer_notifications.xlsx'
            with pd.ExcelWriter(response, engine = 'xlsxwriter') as writer:
                df.to_excel(writer, index = False, sheet_name = 'Observer Notifications')

            # Return excel to user
            return response
        except Exception as e:
            messages.error(request, f"Unable to export observer notificaitons: {e}")
            return redirect("home")


# List registered OrgUsers
def list_users(request):
    users = OrgUser.objects.all()
    return render(request, 'list_users.html', {'users':users})