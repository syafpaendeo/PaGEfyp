import re
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.popup import Popup
from kivy_garden.zbarcam import ZBarCam

# Set background color
Window.clearcolor = (0.9, 0.9, 0.9, 1)

# Function to validate date
def is_valid_date(date_str):
    pattern = r'^\d{2}/\d{2}/\d{4}$'
    if not re.match(pattern, date_str):
        return False
    try:
        datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='logindb navi',
        user='root',
        password=''
    )

# Employee Registration Screen
class EmployeeRegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.top_nav_image = Image(source='logo_PaGE.png', size_hint=(1, None), height=150)
        self.layout.add_widget(self.top_nav_image)

        self.layout.add_widget(Label(text="Welcome", font_size=20, color=(0, 0, 0, 1)))
        self.layout.add_widget(Label(text="SIGN UP", font_size=20, color=(0, 0, 0, 1)))

        self.layout.add_widget(Label(text="Email*", color=(0, 0, 0, 1)))
        self.email_input = TextInput(multiline=False)
        self.layout.add_widget(self.email_input)

        self.error_label = Label(text="", color=(1, 0, 0, 1))  # Red text for errors
        self.layout.add_widget(self.error_label)

        self.layout.add_widget(Label(text="Password*", color=(0, 0, 0, 1)))
        self.password_input = TextInput(multiline=False, password=True)
        self.layout.add_widget(self.password_input)

        self.layout.add_widget(Label(text="Date Of Birth*", color=(0, 0, 0, 1)))
        self.dob_picker_button = Button(text="Select Date")
        self.dob_picker_button.bind(on_release=self.show_date_picker)
        self.layout.add_widget(self.dob_picker_button)

        self.dob_label = Label(text="No date selected", color=(0, 0, 0, 1))
        self.layout.add_widget(self.dob_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        button_layout.add_widget(Label(text=""))  # Spacer
        self.register_button = Button(text="SIGN UP", size_hint=(None, None), size=(200, 50), on_release=self.register)
        button_layout.add_widget(self.register_button)
        button_layout.add_widget(Label(text=""))  # Spacer
        self.layout.add_widget(button_layout)

        sign_in_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=10)
        sign_in_layout.add_widget(Label(text="Already have an account? ", color=(0, 0, 0, 1)))
        
        self.sign_in_button = Button(text="Sign In", size_hint=(None, None), size=(100, 30))
        self.sign_in_button.bind(on_release=self.go_to_sign_in)
        sign_in_layout.add_widget(self.sign_in_button)

        sign_in_layout.size_hint_x = None
        sign_in_layout.width = 300
        sign_in_layout.pos_hint = {'center_x': 0.5}
        self.layout.add_widget(sign_in_layout)

        self.add_widget(self.layout)

    def show_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected, on_cancel=self.on_date_cancelled)
        date_dialog.open()

    def on_date_selected(self, instance, value, *args):
        self.dob_label.text = f"Selected Date: {value.strftime('%d/%m/%Y')}"

    def on_date_cancelled(self, instance, *args):
        self.dob_label.text = "No date selected"

    def register(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        dob = self.dob_label.text.replace("Selected Date: ", "")

        if not is_valid_email(email):
            self.error_label.text = "Invalid email address."
        elif not is_valid_date(dob):
            self.error_label.text = "Invalid date format. Please use DD/MM/YYYY."
        else:
            self.error_label.text = ""
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                
                # Check if the email already exists in the database
                cursor.execute("SELECT * FROM login WHERE email = %s", (email,))
                result = cursor.fetchone()
                
                if result:
                    self.error_label.text = "The email already exists."
                else:
                    # Email doesn't exist, proceed to insert the new user
                    cursor.execute("""
                        INSERT INTO login (email, password, date) 
                        VALUES (%s, %s, %s)
                    """, (email, password, datetime.strptime(dob, '%d/%m/%Y').date()))
                    connection.commit()

                    sign_in_screen = self.manager.get_screen('sign_in_screen')
                    sign_in_screen.saved_email = email
                    sign_in_screen.saved_password = password
                    self.manager.current = 'sign_in_screen'

                cursor.close()
                connection.close()

            except Error as e:
                self.error_label.text = f"Error: {e}"

    def go_to_sign_in(self, instance):
        self.manager.current = 'sign_in_screen'

# Sign In Screen
class SignInScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content_layout = BoxLayout(orientation='vertical', spacing=10, padding=[10, 20, 10, 20], size_hint=(1, 1))
        content_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        content_layout.add_widget(Label(text="Sign In", font_size=20, color=(0, 0, 0, 1), size_hint_y=None, height=40))

        content_layout.add_widget(Label(text="Email*", color=(0, 0, 0, 1), size_hint_y=None, height=30))
        self.email_input = TextInput(multiline=False, size_hint_y=None, height=40, size_hint_x=1)
        content_layout.add_widget(self.email_input)

        content_layout.add_widget(Label(text="Password*", color=(0, 0, 0, 1), size_hint_y=None, height=30))
        self.password_input = TextInput(multiline=False, password=True, size_hint_y=None, height=40, size_hint_x=1)
        content_layout.add_widget(self.password_input)

        self.sign_in_button = Button(text="SIGN IN", size_hint=(None, None), size=(200, 50), on_release=self.sign_in)
        self.sign_in_button.pos_hint = {'center_x': 0.5}
        content_layout.add_widget(self.sign_in_button)

        self.error_label = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30, size_hint_x=1)
        content_layout.add_widget(self.error_label)

        self.back_to_signup_button = Button(text="Back to Sign Up", size_hint=(None, None), size=(200, 50), on_release=self.go_back_to_signup)
        self.back_to_signup_button.pos_hint = {'center_x': 0.5}
        content_layout.add_widget(self.back_to_signup_button)

        self.layout.add_widget(content_layout)
        self.add_widget(self.layout)

    def sign_in(self, instance):
        email = self.email_input.text
        password = self.password_input.text

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM login WHERE email = %s", (email,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result and result[0] == password:
                self.error_label.text = ""
                self.manager.current = 'home_screen'
            else:
                self.error_label.text = "Invalid email or password."
        except Error as e:
            self.error_label.text = f"Error: {e}"

    def go_back_to_signup(self, instance):
        self.manager.current = 'registration_screen'
# Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.main_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.main_content.add_widget(Label(text="Home", font_size=20, color=(0, 0, 0, 1)))
        self.main_content.add_widget(Label(text="Welcome to the Home Screen.", color=(0, 0, 0, 1)))

        # Bottom navigation layout
        self.bottom_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.bottom_nav.add_widget(Button(text="Home", on_release=self.go_home))
        self.bottom_nav.add_widget(Button(text="SCAN HERE", on_release=self.go_to_scan))
        self.bottom_nav.add_widget(Button(text="Profile", on_release=self.go_profile))

        self.layout.add_widget(self.main_content)
        self.layout.add_widget(self.bottom_nav)
        self.add_widget(self.layout)

    def go_home(self, instance):
        pass  # Already on Home screen

    def go_profile(self, instance):
        self.manager.current = 'profile_screen'

    def go_to_scan(self, instance):
        self.manager.current = 'qr_scan_screen'

# QR Scan Screen
class QRScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        self.zbarcam = ZBarCam()
        self.zbarcam.bind(on_code=self.on_qr_code_scanned)  # Bind to QR code scan event
        self.layout.add_widget(self.zbarcam)

        # Bottom navigation layout
        self.bottom_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.bottom_nav.add_widget(Button(text="Home", on_release=self.go_home))
        self.bottom_nav.add_widget(Button(text="SCAN HERE", on_release=self.go_to_scan))
        self.bottom_nav.add_widget(Button(text="Profile", on_release=self.go_profile))

        self.layout.add_widget(self.bottom_nav)
        self.add_widget(self.layout)

    def on_qr_code_scanned(self, instance, value):
        self.show_qr_popup(value)

    def show_qr_popup(self, qr_data):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text="Scanned QR Code Data:", font_size=18))
        popup_content.add_widget(Label(text=qr_data, font_size=16))
        
        close_button = Button(text="Close", size_hint_y=None, height=50)
        close_button.bind(on_release=self.close_popup)
        popup_content.add_widget(close_button)
        
        self.popup = Popup(title="QR Code Data", content=popup_content,
                           size_hint=(None, None), size=(400, 300))
        self.popup.open()

    def close_popup(self, instance):
        self.popup.dismiss()

    def go_home(self, instance):
        self.manager.current = 'home_screen'

    def go_to_scan(self, instance):
        pass  # Already on QR Scan screen

    def go_profile(self, instance):
        self.manager.current = 'profile_screen'

# Profile Screen
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # User Info Section
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.user_name_label = Label(text="User Full Name", font_size=20, color=(0, 0, 0, 1))
        self.user_name_label.bind(on_release=self.go_to_edit_profile)
        self.user_info_layout.add_widget(self.user_name_label)

        # Add an "Edit Profile" button
        self.edit_profile_button = Button(text="Edit Profile", size_hint_y=None, height=50)
        self.edit_profile_button.bind(on_release=self.go_to_edit_profile)
        self.user_info_layout.add_widget(self.edit_profile_button)
        
        self.layout.add_widget(self.user_info_layout)
        self.layout.add_widget(Label(text="User profile information goes here.", color=(0, 0, 0, 1)))

        # Bottom navigation layout
        self.bottom_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.bottom_nav.add_widget(Button(text="Home", on_release=self.go_home))
        self.bottom_nav.add_widget(Button(text="SCAN HERE", on_release=self.go_to_scan))
        self.bottom_nav.add_widget(Button(text="Profile", on_release=self.go_profile))

        self.layout.add_widget(self.bottom_nav)
        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.update_user_name()

    def update_user_name(self):
        # Fetch and update the user's full name from the database or shared data
        self.user_name_label.text = "Updated Full Name"  # Replace with actual logic to get the updated name

    def go_home(self, instance):
        self.manager.current = 'home_screen'

    def go_profile(self, instance):
        pass  # Already on Profile screen

    def go_to_scan(self, instance):
        self.manager.current = 'qr_scan_screen'

    def go_to_edit_profile(self, instance):
        self.manager.current = 'edit_profile_screen'

# Edit Profile Screen
class EditProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Back button
        back_button = Button(text="Back", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)

        self.layout.add_widget(Label(text="Edit Profile", font_size=20, color=(0, 0, 0, 1)))

        self.layout.add_widget(Label(text="Full Name*", color=(0, 0, 0, 1)))
        self.full_name_input = TextInput(multiline=False)
        self.layout.add_widget(self.full_name_input)

        self.layout.add_widget(Label(text="Gender*", color=(0, 0, 0, 1)))
        self.gender_input = TextInput(multiline=False)
        self.layout.add_widget(self.gender_input)

        self.layout.add_widget(Label(text="IC No*", color=(0, 0, 0, 1)))
        self.ic_no_input = TextInput(multiline=False)
        self.layout.add_widget(self.ic_no_input)

        self.layout.add_widget(Label(text="Birthdate*", color=(0, 0, 0, 1)))
        self.birthdate_picker_button = Button(text="Select Date")
        self.birthdate_picker_button.bind(on_release=self.show_date_picker)
        self.layout.add_widget(self.birthdate_picker_button)

        self.birthdate_label = Label(text="No date selected", color=(0, 0, 0, 1))
        self.layout.add_widget(self.birthdate_label)

        self.layout.add_widget(Label(text="Address*", color=(0, 0, 0, 1)))
        self.address_input = TextInput(multiline=False)
        self.layout.add_widget(self.address_input)

        self.layout.add_widget(Label(text="State*", color=(0, 0, 0, 1)))
        self.state_input = TextInput(multiline=False)
        self.layout.add_widget(self.state_input)

        self.layout.add_widget(Label(text="District*", color=(0, 0, 0, 1)))
        self.district_input = TextInput(multiline=False)
        self.layout.add_widget(self.district_input)

        self.layout.add_widget(Label(text="Postcode*", color=(0, 0, 0, 1)))
        self.postcode_input = TextInput(multiline=False)
        self.layout.add_widget(self.postcode_input)

        save_button = Button(text="Save", size_hint_y=None, height=50)
        save_button.bind(on_release=self.save_data)
        self.layout.add_widget(save_button)

        self.add_widget(self.layout)

    def show_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected, on_cancel=self.on_date_cancelled)
        date_dialog.open()

    def on_date_selected(self, instance, value, *args):
        self.birthdate_label.text = f"Selected Date: {value.strftime('%d/%m/%Y')}"

    def on_date_cancelled(self, instance, *args):
        self.birthdate_label.text = "No date selected"

    def save_data(self, instance):
        full_name = self.full_name_input.text
        # Add other fields here
        # Save data to the database or shared storage
        
        # After saving, notify ProfileScreen
        profile_screen = self.manager.get_screen('profile_screen')
        profile_screen.update_user_name()  # Call method to update profile screen

        self.go_back(None)

    def go_back(self, instance):
        self.manager.current = 'profile_screen'


# Main App
class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(EmployeeRegistrationScreen(name='registration_screen'))
        sm.add_widget(SignInScreen(name='sign_in_screen'))
        sm.add_widget(HomeScreen(name='home_screen'))
        sm.add_widget(QRScanScreen(name='qr_scan_screen'))
        sm.add_widget(ProfileScreen(name='profile_screen'))
        sm.add_widget(EditProfileScreen(name='edit_profile_screen'))
        return sm

if __name__ == '__main__':
    MyApp().run()
