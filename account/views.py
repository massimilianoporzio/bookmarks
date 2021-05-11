from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST

from bookmarks.common.decorators import ajax_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib import messages
from .models import Profile, Contact

from django.contrib.auth.decorators import login_required
from actions.utils import create_action
from actions.models import Action


@login_required
def dashboard(request):

    actions = Action.objects.exclude(user=request.user) #mostro le azioni degli ALTRI UTENTI
    following_ids = request.user.following.values_list('id',
                                                       flat=True) #lista degli id utenti che sto seguendo
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user','user__profile').prefetch_related('target')[:10]
            #le prime 10 (e retrieve anche di user e relativo profile) e many to one targets
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})








def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,  # this method check against database
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:  # there is this user on database
                if user.is_active:
                    login(request, user)  # lo associa in sessione
                    return HttpResponse('Authenticated ' \
                                        'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:  # non c'è l'utente su db
                return HttpResponse('Invalid login')
    else:  # non è un POST del form
        form = LoginForm()  # creo nuovo
        return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # creo nuovo utente SENZA salvarlo
            new_user = user_form.save(commit=False)
            # SETTO LA PWD CON IDATI DEL CAMPO password della form
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            # ORA SALVO SU DB
            new_user.save()
            # Create the user profile
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')

            return render(request, 'account/register_done.html',
                          {
                              'new_user': new_user
                          })
    else:
        user_form = UserRegistrationForm()
        return render(request, 'account/register.html',
                      {
                          'user_form': user_form
                      })


@login_required()
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error updating your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
            instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User



@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                        user_to=user)
                create_action(request.user, 'is following', user)

            else:
                Contact.objects.filter(user_from=request.user,
                               user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})



@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section': 'people',
                   'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username,
                             is_active=True)
    contacts = Contact.objects.filter(user_to=user)
    followers = []
    isUserInRequestFollowingUser = False
    for c in contacts:
        followers.append(c.user_from)
    if request.user in followers:
        print("request.user is following user")
        isUserInRequestFollowingUser = True
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                   'isUserInRequestFollowingUser':isUserInRequestFollowingUser,
                   'user': user})
