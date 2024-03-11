"""

project:Oil Monitoring System


"""

from kivy.config import Config
Config.set('kivy','keyboard_mode','dock')
Config.set('graphics','fullscreen','auto')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import datetime
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import tansensor_modbus
import json
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg, FigureCanvas
import matplotlib.pyplot as plt
from database import OilMonitoringData, AlarmConfigData
import sendemail
import send_sms

import threading
from functools import partial

from read_rtc_time import read_rtc_datetime
import set_rtc_time


#build the load_file to connect the gui from python to kv design files
Builder.load_file("homescreen.kv")
Builder.load_file("sensordatascreen.kv")
Builder.load_file("loghistoryscreen.kv")
Builder.load_file("graphplotscreen.kv")
Builder.load_file("settingscreen.kv") 




sound_file_path = 'D:/CEPL/beep.mp3'

button_click_sound = SoundLoader.load(sound_file_path)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def callback(self, event):
        self.play_button_sound()
    
    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
            print(f"Error:playing the sound:{e}")
    """
    def on_start(self):
        
    
        get_tank_id = self.ids.tank.text.strip()

        if get_tank_id and not get_tank_id.isalnum():
            self.show_alert("Please enter a valid alphanumeric tank ID.")
            return

        self.manager.get_screen("FirstScreen").update_tank_id(get_tank_id)
        self.manager.get_screen("SecondScreen").update_tank_id(get_tank_id)
        self.manager.get_screen("ThirdScreen").update_tank_id(get_tank_id)
        self.manager.get_screen("FourthScreen").update_tank_id(get_tank_id)

    """
    def input_valid(self):
        # Check if the input box contains the required values

        get_tank_id = self.ids.tank.text.strip()

        if get_tank_id:
            return 1
        


    def next_screen(self):

        get_tank_id = self.ids.tank.text.strip()
        if self.input_valid():
            # Transition to the next screen
            self.manager.current = 'FirstScreen'
            self.manager.get_screen("FirstScreen").update_tank_id(get_tank_id)
            self.manager.get_screen("SecondScreen").update_tank_id(get_tank_id)
            self.manager.get_screen("ThirdScreen").update_tank_id(get_tank_id)
            self.manager.get_screen("FourthScreen").update_tank_id(get_tank_id)
        else:
            # Show alert or handle invalid input
            self.show_alert("Please Enter The Tank ID !")
        
    
        
        
   



    

    
    def show_alert(self, message):
        alert_popup = Popup(title='Alert',
                            title_color = (0,0,0,1),
                    
                             background = '',
                             background_color = (217/255,217/255,217/255,1),

                             content=Label(text=message, color = (0,0,0,1), font_size = 30), 
                             size_hint=(None, None), 
                             size=(500, 200))
        alert_popup.open()



      
        

    
    def motor_on(self):

        self.ids.on.text  = f"MOTOR ON"
        opacity_value_off = self.ids.off
        opacity_value_off.opacity = 0

        opacity_value_off = self.ids.on
        opacity_value_off.opacity = 1

        
        

    def motor_off(self):
        self.ids.off.text = f"MOTOR OFF"
        opacity_value_on= self.ids.on
        opacity_value_on.opacity = 0

        opacity_value_on= self.ids.off
        opacity_value_on.opacity = 1

    
    

  

class SensorDataScreen(Screen):
    Window.clearcolor = (1,1,1,1)

    def __init__(self, **kwargs):
        super(SensorDataScreen, self).__init__(**kwargs)
        self.address_Temp_TANN = 0
        self.address_humidity = 34
        self.address_NAS = 56
        self.address_TANN = 6

        self.humidity_register = 1
        self.NAS_register = 1
        self.TANN_register = 1

        self.datastore = OilMonitoringData("oil_monitoring_data.db")

      

        Clock.schedule_interval(self.update_timestamp, 1)
        Clock.schedule_interval(self.update_data, 1)

    
    def update_tank_id(self,get_tank_id):
        self.ids.tank.text = f"TANK ID :{get_tank_id}"
     




    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
           print(f"Error:playing the sound:{e}")
      


    

    
    def update_timestamp(self, dt):
        # Update the timestamp label with the current time
       # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"
  
    def update_data(self, instance):
        try:
            self.port_ICM = "COM12"
            self.port_TANN = "COM13"  # Update this with the correct serial port on your system
           # modbus_baudrate = 9600
           # modbus_unit_id = 1
           # modbus_num_registers = 1


          #  print(tansensor_modbus.read_tansensor('COM12', 19200, 0, 0, 1))
          #  print(tansensor_modbus.read_tansensor('COM12', 19200, 0, 34, 1))
           # print(tansensor_modbus.read_tansensor('COM12', 19200, 0, 56, 6))
          #  print(tansensor_modbus.read_tansensor('COM12', 19200, 0, 34, 1))

           # self.NAS_data = tansensor_modbus.read_tansensor(self.port_ICM, 19200, 0, 56, 6)
            #self.NAS_data = self.read_modbus_registers(self.port_ICM, self.address_NAS, self.NAS_register)
           # self.NAS_data = tansensor_modbus.read_tansensor(self.port_ICM, 19200, 0, 56, 6)
            self.NAS_data = 7
            self.ids.NAS.text = f"{self.NAS_data}"
            
          
            
           # self.temp_data = tansensor_modbus.read_tansensor(self.port_TANN, 9600, 1, 0, 1)
            self.temp_data = 32
            self.ids.oil_temperature.text = f"{self.temp_data/ 100:.2f} °C"
       

           # self.RH_data = tansensor_modbus.read_tansensor(self.port_ICM, 19200, 0, 34, 1 )
            self.RH_data = 72
            self.ids.relative_humidity.text = f"{self.RH_data / 100:.2f} %"
          
    
           # self.TANN_data = tansensor_modbus.read_tansensor(self.port_TANN, 9600, 1, 6, 1)
            self.TANN_data = 4
            self.ids.TANN.text = f"{self.TANN_data}"
           
            

        except:
            print("NO communication")


    def log_data(self):
        try:
            # Log the current sensor data with timestamp
          #  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          
            timestamp  = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get the tank id
            tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text
 
            threading.Thread(target=self.send_email_if_exceeding, args=(tank_id,)).start()
 
            # Log the current sensor data
            self.datastore.insert_data(
                (
                    timestamp,
                    self.NAS_data,
                    self.TANN_data,
                    self.RH_data,
                    self.temp_data,
                    tank_id
                )
            )
            self.show_alert("Data logged successfully!")
        except ValueError as ve:
            self.show_alert(f"Error logging data: {ve}")

    

    def automatic_log(self):
        hours = self.ids.time_1.text.strip()
        mins = self.ids.time_2.text.strip()

        if mins and not mins.isdigit():
            self.show_alert("Please enter valid numeric values for minutes.")
            return

        if hours and not hours.isdigit():
            self.show_alert("Please enter valid numeric values for hours.")
            return

        if mins:
            mins_int = int(mins)
        else:
            mins_int = 0

        if hours:
            hours_int = int(hours)
        else:
            hours_int = 0

        seconds = hours_int * 60 * 60 + mins_int * 60
        print(seconds)

        if hours_int == 0 and mins_int == 0:
            self.show_alert("Please enter at least one value for hours or minutes.")
            return

        self.show_alert("Automatic log set to {} hours {} minutes!".format(hours_int, mins_int))

        Clock.schedule_interval(partial(self.log_data_periodically), seconds)
            
        



    

    def log_data_periodically(self,dt):
            
            timestamp  = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
       
           # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text
            
            threading.Thread(target=self.send_email_if_exceeding, args=(tank_id,)).start()

            self.datastore.insert_data(
                    (
                        timestamp,
                        self.NAS_data,
                        self.TANN_data,
                        self.RH_data,
                        self.temp_data,
                        tank_id
                    )
                )
    
    
    def send_email_if_exceeding(self, tank_id):

        while App.get_running_app():
            
            serial_port = '/dev/ttyUSB0'
            
            phone_number = '+918618219474'
            
            message = "Alert:Critical Values Exceed"
           
            
            config_store = AlarmConfigData(db_name="oil_monitoring_data.db")

            configured_data = config_store.list_data(tank_id=tank_id)
            if configured_data:
                configured_data = configured_data[0]
            if (
                ( self.NAS_data >= configured_data ["nas_value"] )
                or
                (configured_data["humidity"] and configured_data["humidity"] <= self.RH_data)
                or
                (configured_data["oil_temp"] and configured_data["oil_temp"]  <= self.temp_data)
                or
                (configured_data["tann_value"] and  configured_data["tann_value"] <= self.TANN_data)
            ):

                sendemail.send_email()
                
                send_sms.send_sms(serial_port,phone_number,message)
                   
                
                
            break
        


    def show_alert(self, message):
        alert_popup = Popup(title='Alert',
                            title_color = (0,0,0,1),
                    
                             background = '',
                             background_color = (217/255,217/255,217/255,1),

                             content=Label(text=message, color = (0,0,0,1), font_size = 20), 
                             size_hint=(None, None), 
                             size=(500, 150))
        alert_popup.open()


    def read_modbus_registers(self, port, address, register, baudrate= 9600, bytesize=8, parity='N', stopbits=1,
                              timeout=2):
        client = None
        try:
            client = ModbusSerialClient(
                method='rtu',
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )

            if not client.connect():
                raise ModbusIOException("Failed to connect to Modbus slave")

            result = client.read_holding_registers(address, register, unit=2)

            if result.isError():
                raise ModbusIOException(f"Modbus error: {result}")

            return result.registers

        except ModbusIOException as mie:
            raise mie
        except Exception as e:
            raise e
        finally:
            if client and client.is_socket_open():
                client.close()
            
      
'''
class LogHistoryScreen(Screen):
   # Window.clearcolor = (0, 0, 128, 1)
    

    def __init__(self, **kwargs):
        super(LogHistoryScreen, self).__init__(**kwargs)
        self.datastore = OilMonitoringData("oil_monitoring_data.db")
        Clock.schedule_interval(self.update_timestamp, 1)

    def update_tank_id(self,get_tank_id):
        self.ids.tank.text = f"TANK ID :{get_tank_id}"


      
    
    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
            print(f"Error:playing the sound:{e}")

       

    def update_timestamp(self, dt):
        # Update the timestamp label with the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"


    def view_history(self):


        history_layout = ScrollView()
        history_grid = GridLayout(cols=5, spacing=30, size_hint_y=None)
        history_grid.bind(minimum_height=history_grid.setter('height'))

        header_labels = [ 'Timestamp', 'Oil Temp (°C)',   'RH(%)', 'NAS Value', 'TANN Value']
        for label in header_labels:
            history_grid.add_widget(Label(text=label, color = (0,0,0,1), font_size = 20, ))
        
        tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text

        log_data_list = self.datastore.list_data(tank_id=tank_id)

        for log_entry in log_data_list:
            row_values = [log_entry['timestamp'],
                          f"{log_entry['oil_temp']}",
                          f"{log_entry['humidity']}",
                          f"{log_entry['nas_value']}",
                          f"{log_entry['tann_value']}"]
            for value in row_values:
                history_grid.add_widget(Label(text=value, color=(0,0,0,1), font_size = 15))

        history_layout.add_widget(history_grid)
       # history_popup = Popup( content=history_layout, size_hint=(None, None),size=(1200, 600))
        history_popup = Popup(title='Sensor Data Log History',
                              title_color = (0,0,0,1), 
                               background = '',
                             background_color = (217/255,217/255,217/255,1),
                            content=history_layout,
                            size_hint=(None, None),
                            size=(1200, 600))
        history_popup.open()
    
    
    def clear_log(self):
        tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text
        self.datastore.clear_logs(tank_id=tank_id)

'''


class LogHistoryScreen(Screen):
    
    def __init__(self, **kwargs):
        super(LogHistoryScreen, self).__init__(**kwargs)
        self.datastore = OilMonitoringData("oil_monitoring_data.db")
        Clock.schedule_interval(self.update_timestamp, 1)

    def update_tank_id(self, get_tank_id):
        self.ids.tank.text = f"TANK ID :{get_tank_id}"

    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("Error: loading the sound file")
        except Exception as e:
            print(f"Error: playing the sound: {e}")

    def update_timestamp(self, dt):
        current_time = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"

    def view_history(self):
        history_layout = ScrollView()
        history_grid = GridLayout(cols=5, spacing=30, size_hint_y=None)
        history_grid.bind(minimum_height=history_grid.setter('height'))

        header_labels = ['Timestamp', 'Oil Temp (°C)', 'RH(%)', 'NAS Value', 'TANN Value']
        for label in header_labels:
            history_grid.add_widget(Label(text=label, color=(0, 0, 0, 1), font_size=20))

        tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text

        log_data_list = self.datastore.list_data(tank_id=tank_id)

        for log_entry in log_data_list:
            row_values = [log_entry['timestamp'],
                          f"{log_entry['oil_temp']}",
                          f"{log_entry['humidity']}",
                          f"{log_entry['nas_value']}",
                          f"{log_entry['tann_value']}"]
            for value in row_values:
                history_grid.add_widget(Label(text=value, color=(0, 0, 0, 1), font_size=15))

        history_layout.add_widget(history_grid)
        history_popup = Popup(title='Sensor Data Log History',
                              title_color=(0, 0, 0, 1),
                              background='',
                              background_color=(217 / 255, 217 / 255, 217 / 255, 1),
                              content=history_layout,
                              size_hint=(None, None),
                              size=(1200, 600))
        history_popup.open()

    def clear_log(self):
        confirm_popup = Popup(title='Confirmation',
                              title_color=(0, 0, 0, 1),
                              background='',
                              background_color=(217 / 255, 217 / 255, 217 / 255, 1),
                              size_hint=(None, None),
                              size=(400, 200))

        confirm_label = Label(text="Are you sure you want to clear the log?",
                              color=(0, 0, 0, 1),
                              font_size=20)

        confirm_button = Button(text='Yes',
                                size_hint=(None, None),
                                size=(150, 50))
        cancel_button = Button(text='No',
                               size_hint=(None, None),
                               size=(150, 50))

        def confirm_action(instance):
            tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text
            self.datastore.clear_logs(tank_id=tank_id)
            confirm_popup.dismiss()

        def cancel_action(instance):
            confirm_popup.dismiss()

        confirm_button.bind(on_press=confirm_action)
        cancel_button.bind(on_press=cancel_action)

        confirm_popup.content = BoxLayout(orientation='vertical',
                                          padding=20,
                                          spacing=10)
        confirm_popup.content.add_widget(confirm_label)
        buttons_layout = BoxLayout(spacing=10)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        confirm_popup.content.add_widget(buttons_layout)

        confirm_popup.open()
        

        

    def set_rtc (self):
            
        year =  self.ids.yyyy.text
        month = self.ids.mm.text
        day =   self.ids.dd.text
        hours =  self.ids.hr.text
        minutes =  self.ids.mn.text
        seconds =  self.ids.sc.text
            
       # print(year,month,day,hours,minutes,seconds)
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)
        hours_int = int(hours)
        minutes_int = int(minutes)
        seconds_int = int(seconds)
        
        set_rtc_time.set_rtc_datetime(year_int,month_int,day_int,hours_int,minutes_int,seconds_int)
        
        
    
        
    
      
class GraphPlotScreen(Screen):
    def __init__(self, **kwargs):
        super(GraphPlotScreen, self).__init__(**kwargs)
        self.datastore = OilMonitoringData("oil_monitoring_data.db")
        Clock.schedule_interval(self.update_timestamp, 1)

    def update_tank_id(self,get_tank_id):
        self.ids.tank.text = f"TANK ID :{get_tank_id}"

       
    def update_timestamp(self, dt):
        # Update the timestamp label with the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"
    
    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
            print(f"Error:playing the sound:{e}")

       

    def update_timestamp(self, dt):
        current_time = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"

    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
            print(f"Error:playing the sound:{e}")

    def input_valid(self):
        from_date_input = self.ids.date_from.text
        to_date_input = self.ids.date_to.text

        if not from_date_input and not to_date_input:
            self.show_alert("Please enter a valid date !")
        
        if from_date_input and to_date_input:
            return 1
        
      

        

        
        
    




    def plot_graph(self):

        if self.input_valid():

            from_date_input = self.ids.date_from.text
            to_date_input = self.ids.date_to.text

            print(from_date_input, to_date_input)
            # Get the tank id
            tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text

            if from_date_input and to_date_input:
                tank_data = self.datastore.get_data_within_period(from_date_input, to_date_input, tank_id=tank_id)
            else:
                tank_data = self.datastore.list_data(tank_id)
            timestamp = [sensor_data["timestamp"] for sensor_data in tank_data]
            oil_temp = [sensor_data["oil_temp"] for sensor_data in tank_data]
            humidity = [sensor_data["humidity"] for sensor_data in tank_data]
            nas_value = [sensor_data["nas_value"] for sensor_data in tank_data]
            tan_value = [sensor_data["tann_value"] for sensor_data in tank_data]

            # Create subplots with shared x-axis
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(8, 6))

            # Plotting the graphs on subplots
            ax1.plot(timestamp, oil_temp, label='Oil Temp', color='blue')
            ax2.plot(timestamp, humidity, label='Humidity', color='green')
            ax3.plot(timestamp, nas_value, label='NAS Value', color='orange')
            ax4.plot(timestamp, tan_value, label='TAN Value', color='red')

            # Adding labels to the axes
            ax1.set_ylabel('Oil Temp')
            ax2.set_ylabel('Humidity')
            ax3.set_ylabel('NAS Value')
            ax4.set_ylabel('TAN Value')

            ax1.set_ylim(0, 100)
            ax2.set_ylim(0, 100)
            ax3.set_ylim(0, 15)
            ax4.set_ylim(0, 15)

            # Adding a title to the graph
            fig.suptitle('Oil Monitoring Values Over Time')

            # Adding legends to each subplot
            ax1.legend()
            ax2.legend()
            ax3.legend()
            ax4.legend()

            # Display the graph
            plt.grid()
            

            # Create canvas and add it to the popup content
            canvas = FigureCanvasKivyAgg(plt.gcf())
            content = BoxLayout(orientation='horizontal')
            content.add_widget(canvas)
        

            # Create and open the popup
            popup = Popup(title="Graph",
                        background = '',
                        background_color = (217/255,217/255,217/255,1),
                        content=content,
                        size_hint=(None, None),
                        size=(1200, 600))
            popup.open()
        
    def show_alert(self, message):
        alert_popup = Popup(title='Alert',
                        title_color = (0,0,0,1),
                
                            background = '',
                            background_color = (217/255,217/255,217/255,1),

                            content=Label(text=message, color = (0,0,0,1), font_size = 30), 
                            size_hint=(None, None), 
                            size=(500, 150))
        alert_popup.open()
    
    

            
                

class SettingScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)

        Clock.schedule_interval(self.update_timestamp, 1)

    def update_tank_id(self,get_tank_id):
        self.ids.tank.text = f"TANK ID :{get_tank_id}"
       

    def update_timestamp(self, dt):
        
        current_time = read_rtc_datetime().strftime("%Y-%m-%d %H:%M:%S")
        self.ids.timestamp_label.text = f" {current_time}"


    
    def callback(self, event):
        self.play_button_sound()

    def play_button_sound(self):
        try:
            sound = SoundLoader.load('D:/CEPL/beep.mp3')
            if sound:
                sound.play()
            else:
                print("error:loading the sound file")
        except Exception as e:
            print(f"Error:playing the sound:{e}")

    
    def on_submit(self):
        get_nas_value = self.ids.nas_value.text
       # print(get_nas_value)
        get_rh_value = self.ids.rh_value.text
        get_oil_temp_value = self.ids.oil_temp_value.text
        get_tann_value = self.ids.tann_value.text
        tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text


        config_store = AlarmConfigData(db_name="oil_monitoring_data.db")

        # Get the tank id
        tank_id = self.manager.get_screen("ZeroScreen").ids.tank.text




        # Log the current sensor data with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        

        config_store.clear_logs(tank_id=tank_id)
        # Log the current sensor data
        config_store.insert_data(
            (
                timestamp,
                get_nas_value,
                get_tann_value,
                get_rh_value,
                get_oil_temp_value,
                tank_id
            )
        )
        
        self.show_alert("Email, Sms will be sent for sensors data exceeding critical values!")
        
        
    def show_alert(self, message):
        alert_popup = Popup(title='Alert',
                            title_color = (0,0,0,1),
                    
                             background = '',
                             background_color = (217/255,217/255,217/255,1),

                             content=Label(text=message, color = (0,0,0,1), font_size = 20), 
                             size_hint=(None, None), 
                             size=(700, 150))
        
        alert_popup.open()


    
class SkfApp(App):

    icon = 'image7.png'
    title = 'SKF OIL MONITORING V1.0'
    def build(self):
        # Create the screen manager
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen (name = "ZeroScreen"))
        sm.add_widget(SensorDataScreen(name="FirstScreen"))
        sm.add_widget(LogHistoryScreen(name="SecondScreen"))
        sm.add_widget(GraphPlotScreen(name="ThirdScreen"))
        sm.add_widget(SettingScreen(name = "FourthScreen"))
        return sm



if __name__ == "__main__":
    SkfApp().run()

