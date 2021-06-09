import phonenumbers
from django.core.paginator import Paginator

from django.db.models.query_utils import Q
from phonenumbers import NumberParseException

from web.models import CommandTrack, MatchRequest, Message, MessageCategory, User, UserDescription, UserDetails

"""
NOTES:

get a Message object and pass it to Penzi class. 
call the Penzi.validate method and save the validation_response

check if the validation_response contains a key called 'category'
If it has, create a Process object and pass the validation_response as parameter to the constructor.

call the Process.process method to process the user validated_response and save the response.
Check if the response has a key called 'reply'
if there is, access the 'messages' key from the response, and send the value to the user. 
messages is a list

"""


class PenziQuery:
    """
    PenziQuery class takes in a MatchRequest object and makes a query for the criteria specified. Then constructs
    appropriate messages to reply to the user.
    """

    def __init__(self, request: MatchRequest) -> None:
        """
        @param request: a MatchRequest instance
        """
        self.request = request
        if self.request.user.gender == "male":
            self.title = "lady"
            self.pronoun = "her"
            self.refer = "her"
            self.title_plural = "ladies"
        else:
            self.title = "gent"
            self.pronoun = "him"
            self.refer = "his"
            self.title_plural = "gents"

    def _get_match(self):
        # check user request
        town_match = User.objects.filter(Q(town__icontains=self.request.town) | Q(county__icontains=self.request.town))

        if self.request.lower_age is not None:
            age_match = town_match.filter(age__range=(self.request.lower_age, self.request.upper_age))
        else:
            age_match = town_match.filter(age=self.request.upper_age)

        if self.request.user.gender == "male":
            match = age_match.filter(gender="female")
        else:
            match = age_match.filter(gender="male")
        return match

    def paginated_match(self):
        # gets a subset of the match result,
        _matches = self._get_match()
        p = Paginator(_matches, 3)
        page = p.page(self.request.page)

        return {
            'page': page,
            'matches': _matches
        }

    def request_next(self):
        if self.request.page == 0:
            msg = "There are no more results"
        else:
            res = self.paginated_match()
            msg = ""
            for item in res["page"].object_list:
                msg += f"Name: {item.full_name}\nAge: {item.age}\nPhone: {item.phone}\n\n"
            # VERY IMPORTANT ### INCREMENT PAGE ###
            if res["page"].has_next():
                msg += " \nSend NEXT to see more results"
                self.request.page += 1
            else:
                self.request.page = 0
            self.request.save()
        return msg

    def generate_message(self):
        messages = []
        res = self.paginated_match()

        print(f"all matches: {res['matches']}")
        if res["matches"].count() == 0:
            message = f"We couldn't find {self.title_plural} matching your criteria. Try again later."
        elif res["matches"].count() == 1:
            message = f"We have 1 {self.title} who match your choice! We will send you the details. To get more " \
                      f"details about a {self.pronoun}, SMS {self.refer} number EG 0722123456 to 5001 "
        elif res["matches"].count() <= 3:
            message = f"We have {res['matches'].count()} {self.title_plural} who match your choice. We will send " \
                      f"you their details shortly. To get more details about a {self.pronoun}, SMS {self.refer} " \
                      f"number EG 0722123456 to 5001 "
        else:
            message = f"We have {res['matches'].count()} {self.title_plural} who match your choice. We will send " \
                      f"you details of 3 of them shortly. To get more details about a {self.pronoun}, SMS {self.refer}"\
                      f" number EG 0722123456 to 5001 "

        messages.append(message)

        second_message = ""
        for item in res['page'].object_list:
            second_message += f"Name: {item.full_name}\nAge: {item.age}\nPhone: {item.phone}\n\n"

        # VERY IMPORTANT ### INCREMENT PAGE ###
        if res['page'].has_next():
            second_message += " \n\nSend NEXT to see more results"
            self.request.page += 1
        else:
            self.request.page = 0
        self.request.save()

        if second_message != "":
            messages.append(second_message)

        return messages


class Penzi:
    def __init__(self, message: Message):
        self.message = message

    def _is_phone(self):
        text = self.message.text
        try:
            phonenumbers.parse(text, 'KE')
        except NumberParseException:
            return False
        return True

    def category(self, text=None):
        """
        Categorize text depending on first word
        """
        if text is None:
            text = self.message.text
        else:
            text = text

        if text == "penzi":
            return MessageCategory.SERVICE_ACTIVATION
        elif text.startswith("start"):
            return MessageCategory.SERVICE_REGISTRATION
        elif text.startswith("details"):
            return MessageCategory.DETAILS_REGISTRATION
        elif text.startswith("myself"):
            return MessageCategory.SELF_DESCRIPTION
        elif text.startswith("match"):
            return MessageCategory.MATCH_REQUEST
        elif text.startswith("next"):
            return MessageCategory.SUBSEQUENT_MATCH
        elif text.startswith("describe"):
            return MessageCategory.DESCRIPTION_REQUEST
        elif text == "yes":
            return MessageCategory.NOTICE_CONFIRMATION
        elif text == "activate":
            return MessageCategory.RE_ACTIVATION
        if self._is_phone():
            return MessageCategory.MORE_DETAILS

    def validate(self) -> dict:
        """
        Validate formats for each category, 
        returns code 1 if the input is invalid. Else, includes category detected in response
        """
        text = self.message.text.lower()
        category = self.category(text)
        response = {}

        if category == MessageCategory.SERVICE_ACTIVATION:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        elif category == MessageCategory.SERVICE_REGISTRATION:
            # validates length to make sure all details are provided, 
            # also checks age is valid number and gender is valid 
            data = text.split("#")
            if not len(data) == 6:
                response["code"] = 1
                response["desc"] = "invalid registration format"
            elif not data[2].isnumeric():
                response["code"] = 1
                response["desc"] = "invalid age"
            elif not data[3] in ["male", "m", "female", "f"]:
                response["code"] = 1
                response["desc"] = "invalid gender"
            else:
                response["code"] = 0
                response["desc"] = "valid"
                response["category"] = category
                response["message"] = self.message

        elif category == MessageCategory.DETAILS_REGISTRATION:
            # check if text contains excess details. Can accept less details since details
            # are not mandatory
            data = text.split("#")
            if len(data) > 6:
                response["code"] = 1
                response["desc"] = "invalid details format"
            else:
                response["code"] = 0
                response["desc"] = "valid"
                response["category"] = category
                response["message"] = self.message

        elif category == MessageCategory.SELF_DESCRIPTION:
            if self.message.text[1:].strip() is not None:
                response["code"] = 0
                response["desc"] = "valid"
                response["category"] = category
                response["message"] = self.message
            else:
                response["code"] = 1
                response["desc"] = "invalid description format"

        elif category == MessageCategory.MATCH_REQUEST:
            data = text.split("#")
            if not len(data) == 3:
                response["code"] = 1
                response["desc"] = "invalid match format"
            elif "-" in data[1] and len(data[1].split('-')) != 2:
                response["code"] = 1
                response["desc"] = "invalid age range"
            elif "to" in data[1] and len(data[1].split('-')) != 2:
                response["code"] = 1
                response["desc"] = "invalid age range"
            elif "-" in data[1] and (not data[1].split('-')[0].isnumeric or not data[1].split('-')[1].isnumeric):
                response["code"] = 1
                response["desc"] = "invalid age"
            else:
                response["code"] = 0
                response["desc"] = "valid"
                response["category"] = category
                response["message"] = self.message

        elif category == MessageCategory.SUBSEQUENT_MATCH:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        elif category == MessageCategory.DESCRIPTION_REQUEST:
            if len([x for x in text.split(" ") if x != ""]) > 2:
                response["code"] = 1
                response["desc"] = "invalid format"
            else:
                response["code"] = 0
                response["desc"] = "valid"
                response["category"] = category
                response["message"] = self.message

        elif category == MessageCategory.NOTICE_CONFIRMATION:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        elif category == MessageCategory.RE_ACTIVATION:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        elif category == MessageCategory.MORE_DETAILS:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        elif category == MessageCategory.NOTICE_CONFIRMATION:
            response["code"] = 0
            response["desc"] = "valid"
            response["category"] = category
            response["message"] = self.message

        return response


class Process:
    """
    Class for processing user input and messages to be sent back to the user
    """
    def __init__(self, validation: dict):
        """
        Takes a validation result from Penzi.validate
        """
        self.validation = validation

    def exists_user(self):
        phone = self.validation["message"].source
        usr = User.objects.filter(phone=phone)
        return usr.count() > 0

    def update_command_track(self):
        """
        Keeps track of the last command issued by the user.
        """
        if self.exists_user():
            try:
                track = CommandTrack.objects.get(user__phone=self.validation["message"].source)
            except CommandTrack.DoesNotExist:
                CommandTrack.objects.create(
                    user=User.objects.get(phone=self.validation["message"].source),
                    command=MessageCategory.SERVICE_REGISTRATION
                )
                return
            track.command = self.validation["category"]
            track.save()
            return

    def user_describe(self, phone):
        user = User.objects.filter(phone=phone)
        if user.count() > 0:
            user = user.first()
            message = f"{user.full_name}, aged {user.age}, {user.town} town - {user.county} county"
            if len(user.userdetails.education) > 0:
                message += f" {user.userdetails.education},"
            if len(user.userdetails.profession) > 0:
                message += f" {user.userdetails.profession},"
            if len(user.userdetails.marital_status) > 0:
                message += f" {user.userdetails.marital_status},"
            if len(user.userdetails.religion) > 0:
                message += f" {user.userdetails.religion},"
            if len(user.userdetails.tribe) > 0:
                message += f" {user.userdetails.tribe},"

            message += f" Send DESCRIBE {user.phone} to get more details about {user.full_name}"
        else:
            message = ""

        return message

    def process(self) -> dict:
        phone = self.validation["message"].source
        if "category" not in self.validation:
            return {"action": "noreply", "messages": ["Unvalidated input"]}

        category = self.validation["category"]
        data = self.validation["message"]
        response = {}

        exists = self.exists_user()
        if category == MessageCategory.SERVICE_ACTIVATION and not exists:
            response["action"] = "reply"
            response["messages"] = [
                "Welcome to our dating service with 6000 potential dating partners! To register, "
                "sms start#name#age#sex#county#town to 5001 E.G start#Mike#26#Male#kisii#ogembo"]

        elif category == MessageCategory.SERVICE_ACTIVATION and exists:
            response["action"] = "reply"
            response["messages"] = [
                "You are now registered! Enjoy yourself. To search for a MPENZI, SMS Match#age#town to 5001 E.G "
                "Match#23-25#Nairobi"]

        elif category == MessageCategory.SERVICE_REGISTRATION and not exists:

            text = data.text.split("#")
            gender = text[3]

            # save gender in same format
            if gender in ["m", "male"]:
                gender = "male"
            else:
                gender = "female"

            # register user to the system
            user = User()

            user.phone = data.source
            user.full_name = text[1]
            user.age = int(text[2])
            user.gender = gender
            user.county = text[4]
            user.town = text[5]
            user.save()

            response["action"] = "reply"
            response["messages"] = [
                "Thank You. SMS details#level of education#profession#marital status#religion#tribe to 5001 E.G "
                "details#diploma#accountant#single#christian#mijikenda"]

        elif not exists:

            response["action"] = "noreply"
            response["messages"] = ["User not registered"]

        elif category == MessageCategory.SERVICE_REGISTRATION:
            response["action"] = "reply"
            response["messages"] = [
                "You are now registered! Enjoy yourself. To search for a MPENZI, SMS Match#age#town to 5001 E.G "
                "Match#23-25#Nairobi"]

        elif category == MessageCategory.DETAILS_REGISTRATION:
            text = data.text.split("#")
            user = User.objects.get(phone=phone)

            dets = UserDetails.objects.get(user=user)

            dets.education = text[1]
            dets.profession = text[2]
            dets.marital_status = text[3]
            dets.religion = text[4]
            dets.tribe = text[5]
            dets.save()

            response["action"] = "reply"
            response["messages"] = [
                "This is the last stage of registration. SMS a brief description of yourself to 5001 starting with "
                "the word MYSELF E.G MYSELF chocolate, lovely, sexy etc"]

        elif category == MessageCategory.SELF_DESCRIPTION:
            text = [x for x in data.text.split(" ") if x != ""]
            user = User.objects.get(phone=phone)

            desc = UserDescription.objects.get(user=user)
            desc.description = text[1]

            response["action"] = "reply"
            response["messages"] = [
                "You are now registered! Enjoy yourself. To search for a MPENZI, SMS Match#age#town to 5001 E.G "
                "Match#23-25#Nairobi"]

        elif category == MessageCategory.MATCH_REQUEST:
            text = data.text.split("#")
            user = User.objects.get(phone=phone)
            town = text[2]

            if "-" in text[1]:
                lower, upper = text[1].split("-")
            else:
                upper = text[1]
                lower = None

            match = MatchRequest()
            match.user = user
            if lower is not None:
                match.lower_age = int(lower)
            match.upper_age = int(upper)
            match.town = town
            match.save()
            match.refresh_from_db()

            messages = PenziQuery(match).generate_message()

            response["action"] = "reply"
            response["messages"] = messages

        elif category == MessageCategory.SUBSEQUENT_MATCH:
            user = User.objects.get(phone=phone)

            match = MatchRequest.objects.filter(user=user).last()
            message = PenziQuery(match).request_next()

            response["action"] = "reply"
            response["messages"] = [message]

        elif category == MessageCategory.MORE_DETAILS:

            search_term = int(phonenumbers.format_number(
                phonenumbers.parse(data.text, 'KE'),
                phonenumbers.PhoneNumberFormat.E164
            )[1:])

            message = self.user_describe(search_term)
            if message is None:
                response["action"] = "noreply"
                response["messages"] = ["User not found"]

            else:
                response["action"] = "reply"
                response["messages"] = [message]

        elif category == MessageCategory.DESCRIPTION_REQUEST:
            searched_desc = [x for x in data.text.split(" ") if x != ""][1]

            result = User.objects.filter(phone=searched_desc)
            if not result.count() > 0:
                response["action"] = "reply"
                response["messages"] = ["Phone searched was not found. Try again"]
            else:
                result = result.first()
                response["action"] = "reply"
                if len(result.userdescription.description.strip()) == 0:
                    response["messages"] = [f"{result.full_name} has not set a description"]
                else:
                    response["messages"] = [f"{result.userdescription.description}"]
                response["searched_user"] = result

        elif category == MessageCategory.RE_ACTIVATION:
            response["action"] = "reply"
            response["messages"] = [
                "You are now registered! Enjoy yourself. To search for a MPENZI, SMS Match#age#town to 5001 E.G "
                "Match#23-25#Nairobi"]

        elif category == MessageCategory.NOTICE_CONFIRMATION:
            last_message = Message.objects.filter(destination=phone).last()
            print(f"NOTICE CONFIRMATION SOURCE LAST MESSAGE: {last_message}")
            if 'is interested in you' in last_message.text:
                search = Message.objects.filter(text__istartswith='describe').filter(text__contains=phone).last().source
                message = self.user_describe(search)
                response["action"] = 'reply'
                response["messages"] = [message]

        self.update_command_track()
        return response
