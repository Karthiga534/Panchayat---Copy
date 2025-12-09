from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import *
import json
from django.contrib import messages
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import random
from django.contrib.auth.hashers import make_password
from .models import Signup
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie,  csrf_exempt
from django.views.decorators.http import require_POST
# from .serializers import (
#     SignupSerializer, UserSerializer,
#     ComplaintSerializer, RequestSerializer,
#     NotificationSerializer, ActivitySerializer
# )

# =========================
# ROLE-BASED SIGNUP
# =========================
 # Make sure your model is imported

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        phone = request.POST.get("phoneno")
        password = request.POST.get("password")
        conpass = request.POST.get("conpass")
        address = request.POST.get("address")

        # Validation
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "signuppage.html", {
                "username": username,
                "phoneno": phone,
                "address": address
            })

        if password != conpass:
            messages.error(request, "Passwords do not match.")
            return render(request, "signuppage.html", {
                "username": username,
                "phoneno": phone,
                "address": address
            })

        # Save new user
        new_user = Signup(
            username=username,
            phoneno=phone,
            password=password,
            conpass=conpass,
            address=address
        )
        new_user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect("loginpage")  # URL name of your login page

    # GET request
    return render(request, "signuppage.html")


def welcome(request):
    return render(request, "Welcomepage.html")
def welcome2(request):
    return render(request, "Welcomeadmin.html")
def welcome3(request):
    return render(request, "Welcomesupervisor.html")
def welcome4(request):
    return render(request, "Welcomeeo.html")

def Startpage(request):
    return render(request, "Startpage.html")

def loginpage(request):
    if request.method == "POST":
        phoneno = request.POST.get("phoneno")
        password = request.POST.get("password")

        user = Signup.objects.filter(phoneno=phoneno, password=password).first()

        if user:
            # Store info in session
            request.session['username'] = user.username
            request.session['phoneno']=phoneno
            # Log the login
            new_det = Login(username=user.username, phoneno=phoneno, password=password, role="public")
            new_det.save()

            messages.success(request, "✅ Login Successful!")

            # ✅ Redirect to Mainpage view instead of rendering directly
            return redirect('Mainpage')  # 'mainpage' should be the URL name of your Mainpage view

        else:
            messages.error(request, "❌ Invalid username or password.")
            return redirect("loginpage")

    return render(request, "loginpage.html")

def loginpage2(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)

        # Try to find a matching admin
        user = Admins.objects.filter(username=username, password=password).first()
        new_det=Login(username=username,password=password,role="admin")
        new_det.save()
        
        if user:
            request.session['admin_username'] = user.username
            messages.success(request, "✅ Login Successful!")
            return redirect("Mainpageadmin")
        else:
            messages.error(request, "❌ Invalid username or password.")
            return render(request, "loginpageadmin.html")
    return render(request, "loginpageadmin.html")
def loginpage3(request):
    if request.method=="POST":
        supervisor_name=request.POST.get("username")
        password=request.POST.get("password")

        user=Supervisor.objects.filter(supervisor_name=supervisor_name, password=password).first()
        new_det=Login(username=supervisor_name,password=password,role="admin")
        new_det.save()
        if user:
            request.session['supervisor_username']=user.supervisor_name
            messages.success(request, "✅ Login Successful!")
            return redirect("Mainsupervisor")
        else:
            messages.error(request, "❌ Invalid username or password.")
            return render(request, "loginsupervisor.html")
    return render(request, "loginsupervisor.html")


def logout(request):
    return render(request, "loginpage.html")
def logout2(request):
    return render(request, "loginpageadmin.html")
def logout3(request):
    return render(request, "loginsupervisor.html")
def logout4(request):
    return render(request, "loginpageeo.html")
# request and complaint
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Complaint, Signup

def complaint_form(request): 
    supervisors = Supervisor.objects.all()  
    area = Area.objects.all()
    complaints = Complaint.objects.all().order_by('-date_time')

    if request.method == "POST":
        # Get form data
        complaintType = request.POST.getlist("complaintType")
        otherType = request.POST.get("otherType")
        description = request.POST.get("description")
        file = request.FILES.get("file")
        date_time = request.POST.get("datetime")  
        username = request.POST.get("user") 
        phone = request.POST.get("phone") 
        address = request.POST.get("address")  
        location = request.POST.get("location") 
        supname = request.POST.get("supervisor_name") 

        # Simple validation
        if not description or not username or not phone or not location:
            messages.error(request, "❌ Please fill in all required fields.")
        else:
            # Handle 'Others'
            if "Others" in complaintType:
                complaint_type_value = otherType
            else:
                complaint_type_value = ", ".join(complaintType)
            
            # Save to database
            new_det=Complaint(
                complaint_type=complaint_type_value,
                description=description,
                file=file,
                date_time=date_time,
                user=username,
                phone=phone,
                address=address,
                location=location,
                supervisor_name=supname
            )
            new_det.save()
            messages.success(request, "✅ Complaint submitted successfully!")
            complaints = Complaint.objects.all().order_by('-date_time')
            return redirect("complaint_form")

    # GET or POST (after saving / validation) - render page with messages
    return render(request, "complaint_form.html", {
        "supervisors": supervisors,
        "area": area,
        "complaints": complaints
    })



# forgot password

otp_store = {}
def Forgotpassword(request):
    if request.method == "POST":
        phoneno = request.POST.get("phoneno")
        try:
            user = Signup.objects.get(phoneno=phoneno)
        except Signup.DoesNotExist:
            return HttpResponse("User not found")

        # Generate OTP
        otp = random.randint(100000, 999999)
        otp_store[phoneno] = otp

        # Send OTP via SMS/email (here just printing for testing)
        print(f"OTP for {phoneno}: {otp}")

        # Redirect to verify OTP page
        return render(request, "verify_otp.html", {"phoneno": phoneno})

    return render(request, "Forgotpassword.html")

# Step 2: Verify OTP and reset password
def verify_otp(request):
    if request.method == "POST":
        phoneno = request.POST.get("phoneno")
        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if str(otp_store.get(phoneno)) != entered_otp:
            return HttpResponse("Invalid OTP")

        if new_password != confirm_password:
            return HttpResponse("Passwords do not match")

        user = Signup.objects.get(phoneno=phoneno)
        user.set_password(new_password)  # This will save the new password
        otp_store.pop(phoneno, None)

        return HttpResponse("Password updated successfully")


# request 

def requestform(request):
    supervisors = Supervisor.objects.all()
    area = Area.objects.all()

    # FIXED: use date_time instead of datetime
    requests = Request.objects.all().order_by('-date_time')

    if request.method == "POST":
        name = request.POST.get("name")
        phone_number = request.POST.get("phone")
        address = request.POST.get("address")
        request_type = request.POST.getlist("requestType")  # multiple values
        file = request.FILES.get("file")
        date_time = request.POST.get("datetime")
        other_type = request.POST.get("otherType")
        location = request.POST.get("location")
        supname = request.POST.get("supervisor_name")

        # Required validation
        if not name or not phone_number or not location:
            messages.error(request, "❌ Please fill in all required fields.")
        else:
            # Check for "Others"
            if "Others" in request_type:
                request_type_value = other_type
            else:
                request_type_value = ", ".join(request_type)

            new_det = Request(
                name=name,
                phone_number=phone_number,
                address=address,
                request_type=request_type_value,
                other_type=other_type,
                area=location,
                supervisor_name=supname,
                file=file,
            )

            new_det.save()
            messages.success(request, "✅ Request submitted successfully!")
            return redirect("requestform")

    return render(request, "request_form.html", {
        "supervisors": supervisors,
        "area": area,
        "requests": requests
    })



# =========================
# MODELS FOR POSTS, ACHIEVEMENTS, TASKS

def Posts(request):
    posts=Post.objects.all().order_by('-created_at')
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        created_at = request.POST.get("datetime") or timezone.now()
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        new_det=Post(
            title=title,
            message=message,
            image=image,
            video=video,
            created_at=created_at
        )
        new_det.save()
        posts=Post.objects.all().order_by('-created_at')
        return redirect('Posts')  # redirect to post list after submission
    return render(request, "posts.html", {"posts": posts})

def Tasks(request):
    supervisors=Supervisor.objects.all()
    areas=Area.objects.all()
    complaints=Complaint.objects.all()
    requests=Request.objects.all()
    return render(request, "task.html",{"supervisors": supervisors,"areas": areas, "complaints":complaints,"requests":requests})    

def Add_supervisor(request):
    supervisors = Supervisor.objects.all()
    areas = Area.objects.all()
    if request.method == "POST":
        supervisor_name = request.POST.get('supervisor_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        supervisor_id = request.POST.get('supervisor_id')
        area = request.POST.get('area')
        password = request.POST.get('password')
        conpass = request.POST.get('conpass')

        # Password validation
        if password != conpass:
            messages.error(request, " ❌ Passwords do not match!")
            return redirect('Add_supervisor')

        # Optional: check if phone or supervisor_id already exists
        if Supervisor.objects.filter(phone=phone).exists():
            messages.error(request, " ❌ Phone number already exists!")
            return redirect('Add_supervisor')

        if Supervisor.objects.filter(supervisor_id=supervisor_id).exists():
            messages.error(request, " ❌ Supervisor ID already exists!")
            return redirect('Add_supervisor')

        # Save the Supervisor to DB
        supervisor = Supervisor(
            supervisor_name=supervisor_name,
            phone=phone,
            address=address,
            gender=gender,
            supervisor_id=supervisor_id,
            area=area,
            password=password,
            conpass=conpass
        )
        supervisor.save()
        supervisors=Supervisor.objects.all()
        areas=Area.objects.all()
        messages.success(request, " ✅ Supervisor added successfully!")
        return redirect('Add_supervisor')

    return render(request, 'Addsupervisor.html',{"supervisors":supervisors, "areas":areas})

def Add_area(request):
    areas = Area.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        if Area.objects.filter(name=name).exists():
            return redirect('/addarea/?message=exists')
        else:
            new_det = Area(name=name)
            new_det.save()
            return redirect('/addarea/?message=added')
            areas = Area.objects.all()
        # ✅ Use redirect so the message displays properly and doesn't repeat on refresh
        
    return render(request, "Add_area.html", {"areas": areas})

def Delete_area(request):
    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        try:
            area = Area.objects.get(id=area_id)
            area.delete()
            return redirect('/addarea/?message=deleted')
        except Area.DoesNotExist:
            return redirect('Add_area')
    return redirect('Add_area')

@login_required
def upload_profile(request):
    if request.method == "POST" and request.FILES.get("profile_image"): # logged-in user
        profile_image = request.FILES["profile_image"]
        new_det=Signup(profile_image=profile_image)
        new_det.save()
        messages.success(request, "✅ Profile updated successfully!")
    else:
        messages.error(request, "❌ No file selected or invalid request!")
    return redirect("Mainpage")

def Mainpage(request):
    username = request.session.get('username')
    phoneno = request.session.get('phoneno')
    print(phoneno)
    user = Signup.objects.get(username=username)
    total_complaints = Complaint.objects.filter(phone=phoneno).count()
    total_requests = Request.objects.filter(phone_number=phoneno).count()
    unverified_complaints = Complaint.objects.filter(phone=phoneno, status='unverified').count()
    verified_complaints = Complaint.objects.filter(phone=phoneno, status='verified').count()
    pending_complaints = Complaint.objects.filter(phone=phoneno, status='pending').count()
    completed_complaints = Complaint.objects.filter(phone=phoneno, status='complete').count()
    unverified_requests = Request.objects.filter(phone_number=phoneno, status='unverified').count()
    verified_requests = Request.objects.filter(phone_number=phoneno, status='verified').count()
    pending_requests = Request.objects.filter(phone_number=phoneno, status='pending').count()
    completed_requests = Request.objects.filter(phone_number=phoneno, status='complete').count()
    print(total_complaints)
    return render(request, "Mainpage.html", {
        "user": user,
        "total_complaints": total_complaints,
        "total_requests": total_requests,
        "phoneno":phoneno,
        'complaints_by_status': {
        'unverified':unverified_complaints,
        'verified': verified_complaints,
        'pending': pending_complaints,
        'complete': completed_complaints
    },
    'requests_by_status': {
        'unverified': unverified_requests,
        'verified': verified_requests,
        'pending': pending_requests,
        'complete': completed_requests
    }
    })

def Mainpageadmin(request):
    admin_username = request.session.get('admin_username', None)
    total_complaints = Complaint.objects.all().count()
    total_requests = Request.objects.all().count()
    total_supervisors = Supervisor.objects.count()
    total_eo = EOSignup.objects.count()
    total_posts = Post.objects.count()
    return render(request, "Mainpageadmin.html", {"admin_username": admin_username, "total_complaints": total_complaints,
        "total_requests": total_requests, "total_supervisors": total_supervisors, "total_eo": total_eo,"total_posts": total_posts,})

def Mainsupervisor(request):
    supervisor_username=request.session.get('supervisor_username', None)
    supervisors=Supervisor.objects.filter(supervisor_name=supervisor_username)
    compcount= Complaint.objects.filter(supervisor_name=supervisor_username, status='unverified').count()
    reqcount= Request.objects.filter(supervisor_name=supervisor_username, status='unverified').count()
    pending_tasks=compcount+reqcount
    for s in supervisors:
        phones = s.phone
        address = s.address
    total_complaints = Complaint.objects.filter(supervisor_name=supervisor_username).count()
    total_requests = Request.objects.filter(supervisor_name=supervisor_username).count()
    return render(request, "Mainsupervisor.html",{"supervisor_username" : supervisor_username, "total_complaints": total_complaints,
        "total_requests": total_requests, "phones":phones, "address":address,'pending_tasks':pending_tasks})

@ensure_csrf_cookie
def complaintsupervisor(request):
    supervisor_username = request.session.get('supervisor_username', None)
    areas = Area.objects.all()
    status = None

    if request.method == "POST":
        status = request.POST.get("status")

    complaints = Complaint.objects.none()  # default empty

    if supervisor_username:
        complaints = Complaint.objects.filter(supervisor_name=supervisor_username)

        if status:  # Only if status is submitted
            for comp in complaints:
                new_det = ComplaintSupervisor(
                    user=comp.user,
                    phone=comp.phone,
                    address=comp.address,
                    location=comp.location,
                    complaint_type=comp.complaint_type,
                    supervisor_name=comp.supervisor_name,
                    status=status
                )
                new_det.save()

    return render(request, "complaintsupervisorpage.html", {
        "complaints": complaints,
        "areas": areas
    })

@require_POST
@csrf_exempt
def toggle_status(request, complaint_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = new_status
        complaint.save()
        return JsonResponse({'success': True, 'status': new_status})
    except Complaint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Complaint not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
@ensure_csrf_cookie
def requestsupervisor(request):
    supervisor_username=request.session.get('supervisor_username', None)
    areas=Area.objects.all()
    status = None

    if request.method == "POST":
        status = request.POST.get("status")
    if supervisor_username:
        requests = Request.objects.filter(supervisor_name=supervisor_username)

        if status:  # Only if status is submitted
            for req in requests:
                new_det = ComplaintSupervisor(
                    user=req.user,
                    phone=req.phone,
                    address=req.address,
                    location=req.location,
                    complaint_type=req.complaint_type,
                    supervisor_name=req.supervisor_name,
                    status=status
                )
                new_det.save()
    return render(request, "requestsupervisorpage.html",{"requests":requests,"areas":areas})

@require_POST
@csrf_exempt
def toggle_request_status(request, request_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')

        # Fetch the request object
        req = Request.objects.get(id=request_id)
        req.status = new_status
        req.save()

        return JsonResponse({'success': True, 'status': new_status})
    except Request.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def notification_page(request):  # Supervisor
    username = request.session.get('supervisor_username')
    if not username:
        return redirect('loginpage3')  # not logged in

    posts = Post.objects.exclude(deleted_by__icontains=username).order_by('-created_at')
    return render(request, "Notificationpage.html", {'posts': posts})


def notification_page2(request):  # for public or supervisor
    username = request.session.get('username')
    if not username:
        return redirect('loginpage')  # not logged in

    posts = Post.objects.exclude(deleted_by__icontains=username).order_by('-created_at')
    return render(request, "Notificationpublic.html", {'posts': posts})
def notification_page3(requests): #EO
    usernumber = requests.session.get('eo_number')
    print(usernumber)
    user=EOSignup.objects.get(eo_number=usernumber)
    if not user:
        return redirect('login4')  # not logged in

    posts = Post.objects.exclude(deleted_by__icontains=usernumber).order_by('-created_at')
    return render(requests, "notification_eo.html", {'posts': posts})
def delete_post(request, post_id):  # Supervisor
    username = request.session.get('supervisor_username')
    if not username:
        return redirect('loginpage3')

    post = get_object_or_404(Post, id=post_id)

    deleted_list = post.deleted_by.split(",") if post.deleted_by else []
    if username not in deleted_list:
        deleted_list.append(username)
        post.deleted_by = ",".join(deleted_list)
        post.save()

    messages.success(request, "🗑️ Notification deleted successfully!")
    return redirect('notification_page')

def delete_post2(request, post_id):
    username = request.session.get('username')
    if not username:
        return redirect('loginpage')

    post = get_object_or_404(Post, id=post_id)

    deleted_list = post.deleted_by.split(",") if post.deleted_by else []
    if username not in deleted_list:
        deleted_list.append(username)
        post.deleted_by = ",".join(deleted_list)
        post.save()

    messages.success(request, "🗑️ Notification deleted successfully!")
    return redirect('notification_page2')
def delete_post4(request, post_id): #EO
    usernumber = request.session.get('eo_number')
    user=EOSignup.objects.get(eo_number=usernumber)
    if not user:
        return redirect('loginpage')

    post = get_object_or_404(Post, id=post_id)

    deleted_list = post.deleted_by.split(",") if post.deleted_by else []
    if usernumber not in deleted_list:
        deleted_list.append(usernumber)
        post.deleted_by = ",".join(deleted_list)
        post.save()

    messages.success(request, "🗑️ Notification deleted successfully!")
    return redirect('notification_page2')
        
def delete_post3(request, post_id): #admin
    username = request.session.get('username')
    if not username:
        return redirect('loginpage')

    post = get_object_or_404(Post, id=post_id)

    deleted_list = post.deleted_by.split(",") if post.deleted_by else []
    if username not in deleted_list:
        deleted_list.append(username)
        post.deleted_by = ",".join(deleted_list)
        post.save()

    messages.success(request, "🗑️ Notification deleted successfully!")
    return redirect('Posts')
 
def Trackstatus(request):
    complaints = Complaint.objects.all()

    return render(request, 'trackstatus.html', {
        'complaints': complaints
    })
def Trackstatus2(request):
    requests_data = Request.objects.all()

    return render(request, 'trackstatus2.html', {
        'requests_data': requests_data
    })
def eo_complaints(request):
    complaints = Complaint.objects.all()
    context = {
        'complaints': complaints,
        'admin_username': request.session.get('eo_emp_number'),
    }
    return render(request, 'eo_complaints.html', context)


def eo_requests(request):
    # Fetch all requests from DB
    requests = Request.objects.all()

    context = {
        'requests': requests 
    }
    return render(request, 'eo_requests.html',context)
def login4(request):
    if request.method == "POST":
        eo_number = request.POST.get("eo_number")
        password = request.POST.get("password")

        user = EOSignup.objects.filter(eo_number=eo_number, password=password).first()
        request.session['eo_number']=eo_number
        if user:
            print("success")
            messages.success(request, "✅ Login Successful!")
            return redirect('eo_dashboard')

  # change to your dashboard URL name
        else:
            print("not success")
            messages.error(request, "❌ Invalid employee number or password.")
            return redirect('login4')

    return render(request, "loginpageeo.html")
def eo_dashboard(request):
    notification_count = Post.objects.count()
    tot_comp= Complaint.objects.count()
    tot_req= Request.objects.count()
    completed_comp= Complaint.objects.filter(status='complete').count()
    completed_req= Request.objects.filter(status='complete').count()
    pending_comp= Complaint.objects.filter(status='pending').count()
    pending_req= Request.objects.filter(status='pending').count()
    usernumber = request.session.get('eo_number')
    eos=EOSignup.objects.filter(eo_number=usernumber)
    return render(request, 'Maineo.html',{'notification_count': notification_count,"eos":eos,"tot_comp":tot_comp,"tot_req":tot_req,"completed_comp":completed_comp,
    "completed_req":completed_req,"pending_comp":pending_comp,"pending_req":pending_req})
def eo_signup(request):
    if request.method == "POST":
        emp_number = request.POST.get("emp_number")
        password = request.POST.get("password")
        conpass = request.POST.get("conpass")

        if password != conpass:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup_EO.html")

        if EOSignup.objects.filter(emp_number=emp_number).exists():
            messages.error(request, "Employee number already exists.")
            return render(request, "signup_EO.html")

        # Save new user (DO NOT include conpass)
        EOSignup(emp_number=emp_number, password=password, conpass=conpass).save()
        messages.success(request, "Signup successful! Please login.")
        return redirect("login4")  # redirect to login page
    return render(request, "signup_EO.html")
def public_signups(request):
    public_users = Signup.objects.all()
    context = {
        'public_users': public_users
    }
    return render(request, 'public_signups.html',context)

def Add_eo(request):
    eos=EOSignup.objects.all()
    areas=Area.objects.all()
    if request.method == "POST":
        eo_number = request.POST.get('eo_number')
        password = request.POST.get('password')
        conpass = request.POST.get('conpass')
        area = request.POST.get('area')
        eo_name = request.POST.get('eo_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if password != conpass:
            messages.error(request, " ❌ Passwords do not match!")
            return redirect('Add_eo')

        if EOSignup.objects.filter(eo_number=eo_number).exists():
            messages.error(request, " ❌ EO number already exists!")
            return redirect('Add_eo')

        new_eo = EOSignup(
            eo_number=eo_number,
            password=password,
            conpass=conpass,
            area=area,
            eo_name=eo_name,
            phone=phone,
            address=address
        )
        new_eo.save()
        messages.success(request, " ✅ EO added successfully!")
        eos=EOSignup.objects.all()
        areas=Area.objects.all()
        return redirect('Add_eo')
    return render(request, "Add_EO.html",{"eos":eos, "areas":areas})
def delete_complaint(request, pk):
    complaint = get_object_or_404(Complaint, id=pk)
    complaint.delete()
    messages.success(request, "Complaint deleted successfully.")
    return redirect("complaint_form")
def achievement(request):
    complaints = Complaint.objects.filter(status='complete')
    requests = Request.objects.filter(status='complete')
    return render(request, "Achievement.html", {"complaints": complaints, "requests": requests})
def Achievementsupervisor(request):
    supervisor_username=request.session.get('supervisor_username', None)
    complaints = Complaint.objects.filter(supervisor_name=supervisor_username, status='verified')
    requests = Request.objects.filter(supervisor_name=supervisor_username, status='verified')
    return render(request, "achievementsupervisor.html", {"complaints": complaints, "requests": requests})

def complaints_eo(request):
    complaints = Complaint.objects.all().order_by('-date_time')
    return render(request, 'complaintseo.html', {'complaints': complaints})
def requests_eo(request):
    requests = Request.objects.all().order_by('-date_time')
    return render(request, 'requestseo.html', {'requests': requests})