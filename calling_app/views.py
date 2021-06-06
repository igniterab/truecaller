from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from .serializers import ContactSerializer
from .models import Contact, CompleteDetails, Profile


@permission_classes((AllowAny,))
class Register(APIView):
    def post(self, request):
        if request.data["name"] is None or request.data["phone_no"] is None:
            return Response(
                {
                    "Error": "Kindly provide both Name and Phone number in order to register with us"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if request.data["email"]:
                email = request.data["email"]
        except:
            email = ""

        user = User(
            username=request.data["phone_no"],
            password=request.data["password"],
            email=email,
        )
        contact = Contact(
            name=request.data["name"],
            phone_no=request.data["phone_no"],
            email=email,
        )
        if user:
            user.set_password(request.data["password"])
            try:
                user.save()
                contact.save()
                profile = Profile.objects.create(
                    user=user,
                    name=request.data["name"],
                    phone_no=request.data["phone_no"],
                    email=email,
                )
                return Response(
                    {
                        "Message": "User Registered successfully"
                    },
                    status=status.HTTP_200_OK
                )
            except:
                return Response(
                    {
                        "Message": "This number is already registered with us kindly try another number"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {
                    "Message": "Something gone wrong during Signup"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes((AllowAny,))
class Login(APIView):
    def post(self, request):
        if not request.data:
            return Response(
                {
                    "Error": "Kindly provide Username and Password to Login"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response(
                {
                    "Error": "Provide both username and password"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        user = authenticate(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "Token": token.key,
                "Message": "User Logged in Success!! , Kindly use this token for further validations and activity"
            },
            status=status.HTTP_200_OK
        )


# If the user wants to add numbers to global db use post or use get to see all numbers in db
class DbContacts(APIView):
    def get(self, request):
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(
            serializer.data
        )

    def post(self, request):
        if request.data["name"] is None or request.data["phone_no"] is None:
            return Response(
                {
                    "Error": "Both name and phone_number are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if request.data["email"]:
                email = request.data["email"]
        except:
            email = ""

        contact = Contact.objects.create(
            name=request.data["name"],
            phone_no=request.data["phone_no"],
            email=email,
        )

        mapping = CompleteDetails.objects.create(
            user=request.user,
            contact=contact,
        )
        return Response(
            {
                "Message": "Contact saved successfully in the global database"
            },
            status=status.HTTP_201_CREATED
        )


class MarkSpam(APIView):
    def post(self, request):
        phone_no = request.data.get("phone_no")
        if request.data["phone_no"] is None:
            return Response(
                {
                    "Error": "Kindly enter the phone number to be marked as spam"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        contact = Contact.objects.filter(
            phone_no=phone_no).update(is_spam=True)
        profile = Profile.objects.filter(
            phone_no=phone_no).update(is_spam=True)

        if (contact or profile):  # this condition here will check for both contact and profile and mark them as spam
            return Response(
                {
                    "Message": "Contact marked as spam successfully!!"
                },
                status=status.HTTP_200_OK
            )
        else:
            # This is the part where the mobile number dosen't mapped to any or doesn't exist in the database

            try:
                if request.data["email"]:
                    email = request.data["email"]
                if request.data["name"]:
                    name = request.data["name"]

            except:
                email = ""
                name = "Spammer-" + str(request.data["phone_no"])

            contact = Contact.objects.create(
                name=name,
                phone_no=request.data["phone_no"],
                email=email,
                is_spam=True,
            )

            return Response(
                {
                    "Message": "This Contact marked as spam and saved in db successfully , Thank you"
                },
                status=status.HTTP_201_CREATED
            )


class SearchPhone(APIView):
    def get(self, request):
        phone_no = request.GET.get("phone_no")
        if phone_no is None:
            return Response(
                {
                    "Error": "Phone number required!!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # profile of the given number
        profile = Profile.objects.filter(phone_no=phone_no)
        email = ""

        # print(profile[0].id)
        # Check if profile exists or not
        if profile:
            # contact list of the given number
            profile_details = CompleteDetails.objects.filter(
                user=profile[0].user)

            # searching the contact list of given number to find if current user is there and if present then show email

            for i in profile_details:
                print(i.contact.phone_no)
                if(str(i.contact.phone_no) == str(request.user)):
                    email = profile[0].email

            user = User.objects.filter(id=profile[0].id, is_active=True)
            return Response(
                {
                    "name": profile[0].name,
                    "phone_no": profile[0].phone_no,
                    "is_spam": profile[0].is_spam,
                    "email": email,
                }
            )
        else:
            contact = Contact.objects.filter(phone_no=phone_no)
            if contact:
                serializer = ContactSerializer(contact, many=True)
                return Response(
                    serializer.data
                )
            else:
                return Response(
                    {
                        "Error": "The given number is not present in the database"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )


class SearchName(APIView):
    def get(self, request):
        name = request.GET.get("name")
        if name is None:
            return Response(
                {
                    "Error": "Kindly provide the name to be searched"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        contact_start = Contact.objects.filter(name__startswith=name)
        contact_contain = Contact.objects.filter(
            name__contains=name).exclude(name__startswith=name)
        response = []

        for contact in contact_start:
            response.append(
                {
                    "name": contact.name,
                    "phone_no": contact.phone_no,
                    "is_spam": contact.is_spam,
                }
            )

        for contact in contact_contain:
            response.append(
                {
                    "name": contact.name,
                    "phone_no": contact.phone_no,
                    "is_spam": contact.is_spam,
                }
            )
        return Response(
            response,
            status=status.HTTP_200_OK
        )
