from .ui import setup_ui
from .model import *


class Controller():

    def __init__(self):
        """Controller class (MVC architecture) that combines model and view of the Audiometer.
        """
        self.selected_program = ""
        program_functions = {"Classic Audiogram:" : self.start_standard_procedure,
                             "Short Screening" : self.start_screen_procedure,
                             "Calibration" : self.start_calibration}
        
        self.calibration_funcs = [self.start_calibration, self.calibration_next_freq, self.calibration_repeat_freq, self.stop_sound, self.calibration_set_level]
        self.view = setup_ui(self.start_familiarization, 
                             program_functions, self.calibration_funcs, self.get_progress)

        # helper variable for calibration
        self.button_changed = False
    
    def run_app(self):
        """Starts the app by running the tkinter mainloop of the view.
        """
        self.view.mainloop()

    def start_familiarization(self, id:str="", headphone:str="Sennheiser_HDA200", calibrate:bool=True, **additional_data)->bool:
        """Creates a Familiarization object and uses it to start the familiarization process.

        Args:
            id (str, optional): ID of test subject. Defaults to "".
            headphone (str, optional): Name of headphone model being used. Defaults to "Sennheiser_HDA200".
            calibrate (bool, optional): Whether to use calibration file. Defaults to True.
            **additional_data: additional key/value pairs to be stored in CSV file after procedure is done

        Returns:
            bool: Whether familiarization was successful
        """
        self.selected_program = "familiarization"
        self.familiarization = Familiarization(id=id, headphone_name=headphone, calibrate=calibrate, **additional_data)
        return self.familiarization.familiarize()

    def start_standard_procedure(self, binaural:bool=False, headphone:str="Sennheiser_HDA200", calibrate:bool=True, **additional_data):
        """Creates a StandardProcedure object and uses it to start the standard procedure.

        Args:
            binaural (bool, optional): Whether to test both ears at the same time. Defaults to False.
            headphone (str, optional): Name of headphone model being used. Defaults to "Sennheiser_HDA200".
            calibrate (bool, optional): Whether to use calibration file. Defaults to True.
            **additional_data: additional key/value pairs to be stored in CSV file after procedure is done
        """
        self.selected_program = "standard"
        self.standard_procedure = StandardProcedure(self.familiarization.get_temp_csv_filename(), headphone_name=headphone, calibrate=calibrate, **additional_data)
        self.standard_procedure.standard_test(binaural)

    def start_screen_procedure(self, binaural:bool=False, headphone:str="Sennheiser_HDA200", calibrate:bool=True, **additional_data):
        """Creates a ScreeningProcedure object and uses it to start the screening procedure.

        Args:
            binaural (bool, optional): Whether to test both ears at the same time. Defaults to False.
            headphone (str, optional): Name of headphone model being used. Defaults to "Sennheiser_HDA200".
            calibrate (bool, optional): Whether to use calibration file. Defaults to True.
            **additional_data: additional key/value pairs to be stored in CSV file after procedure is done
        """
        self.selected_program = "screening"
        self.screen_procedure = ScreeningProcedure(self.familiarization.get_temp_csv_filename(), headphone_name=headphone, calibrate=calibrate, **additional_data)
        self.screen_procedure.screen_test(binaural)

    def start_calibration(self, level:int, headphone:str="Sennheiser_HDA200")->tuple:
        """Creates a Calibration object and uses it to start calibration.

        Args:
            level (int): Level of calibration in dB HL.
            headphone (str, optional): Name of headphone model being used. Defaults to "Sennheiser_HDA200".
        """
        self.selected_program = "calibration"
        self.calibration = Calibration(startlevel=level, headphone_name=headphone)
        _, current_freq, current_spl = self.calibration_next_freq()
        return current_freq, current_spl

    def calibration_next_freq(self)->tuple:
        """Goes to next frequency in calibration process and play it.

        Returns:
            bool: Whether there are more frequencies left after this one.
            int: current frequency
            float: expected SPL value in dB
        """
        more_freqs, current_freq, current_spl = self.calibration.play_one_freq()
        if more_freqs:
            return True, current_freq, current_spl
        elif self.button_changed == False:
            self.button_changed = True
            return False, current_freq, current_spl
        else:
            self.calibration.finish_calibration()
            return False, current_freq, current_spl

    def calibration_repeat_freq(self):
        """Repeats the current frequency during calibration process.
        """
        self.calibration.repeat_freq()

    def calibration_set_level(self, spl:float):
        """Sets the measured level in dB during calbration process.

        Args:
            spl (float): Sound pressure level that was measured in dB
        """
        self.calibration.set_calibration_value(spl)

    def stop_sound(self):
        """Stops the sound during calibration process.
        """
        self.calibration.stop_playing()

    def get_progress(self)->float:
        """Gets current progress in curent procedure for progress bar.

        Returns:
            float: progress value between 0.0 and 1.0
        """
        if self.selected_program == "familiarization":
            return self.familiarization.get_progress()
        elif self.selected_program == "standard":
            return self.standard_procedure.get_progress()
        elif self.selected_program == "screening":
            return self.screen_procedure.get_progress()
        elif self.selected_program == "calibration":
            return 0.0
        else:
            return 0.0

        