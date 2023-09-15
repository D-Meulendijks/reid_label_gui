import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import os
import json
from tkinter import Toplevel
MAX_FILENAME_LENGTH = 8
DESIRED_IMAGE_HEIGHT = 200
DESIRED_IMAGE_WIDTH = 200

DESIRED_ANCHOR_HEIGHT = 200
DESIRED_ANCHOR_WIDTH = 200

DESIRED_SELECTVIEW_HEIGHT = 100
DESIRED_SELECTVIEW_WIDTH = 100
NUMBER_OF_SKIPS = 5

SELECTEDVIEW_ROWS = 10
SELECTEDVIEW_COLUMNS = 10

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")

        self.folder_path_entries = [""] * 5  # Initialize with 5 empty Entry widgets
        self.folder_paths = [""]* 5 # 5 empty strings
        self.image_frames = []
        self.image_labels = []
        self.top_buttons = []
        self.N_top_buttons = []
        self.bottom_buttons = []
        self.N_bottom_buttons = []
        self.image_info = {}  # dict to store image info (click status and folder name for each column)
        self.anchor_infos = []  # List to store anchor info (anchor image name and folder name for each current_id)
        self.image_files_list = ['']*5  # List to store image files for each column
        self.image_files_dates = ['']*5  # List to store image files for each column
        self.current_image_indices = [0, 0, 0, 0, 0]  # Separate current image indices for each column
        self.current_id = 0
        self.current_camera = 0 # [0-4]
        self.date_labels = []  # List to store date labels
        self.anchor_date = "0"

        self.clickable_rows = 5
        self.clickable_columns = 5
        # Set initial values for date_cutoff_start and date_cutoff_end
        self.date_cutoff_start = 10
        self.date_cutoff_end = 4
        self.selectedviewimages_list = []

        # Load or initialize the image info data from a JSON file
        self.load_settings()
        self.load_image_info()
        self.load_anchor_info()

        self.create_root_window()

        self.create_selectedview_window()
        self.create_anchor_window()


        # @@@ Settings
        #self.create_settings_window()
        # Update image clicks and borders to visualize
        self.reload_all_images()
        self.refresh_images()
        
        # @@@ Anchor
        

    def create_root_window(self):
        self.update_anchor_buttons = []
        for i in range(self.clickable_rows):
            for j in range(self.clickable_columns):
                n = j+i*self.clickable_rows

                image_frame = tk.Frame(self.root)
                image_frame.grid(row=1 + i*3, column=j, padx=10, pady=10)
                self.image_frames.append(image_frame)

                image_label = tk.Label(image_frame, text="", padx=10, pady=10)
                image_label.pack()
                image_label.bind("<Button-1>", lambda event, n=n: self.toggle_image_click(n))
                self.image_labels.append(image_label)
                
                image_name_label = tk.Label(image_frame, text="", padx=10)
                image_name_label.pack()

                update_anchor_button = tk.Button(self.root, text=f"Update Anchor {n+1}", command=lambda n=n: self.update_anchor_from_column(n))
                update_anchor_button.grid(row=2 + i*3, column=j)
                self.update_anchor_buttons.append(update_anchor_button)
                date_label = tk.Label(self.root, text="Arbitrary Date", padx=10, pady=10)
                date_label.grid(row=3 + i*3, column=j)
                self.date_labels.append(date_label)

        # @@@ Top frame
        
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, rowspan=9, padx=10, pady=10)

        # @@@ right frame
        self.additional_frame = tk.Frame(self.root)
        self.additional_frame.grid(row=1, column=self.clickable_rows, rowspan=self.clickable_columns, padx=10, pady=10)

        # Create buttons in the new column
        next_all_button = tk.Button(self.additional_frame, text="Next all", command=self.next_all)
        next_all_button.grid(row=0, column=0, padx=10, pady=10)

        move_to_closest_date_button = tk.Button(self.additional_frame, text="Move close to anchor", command=self.move_to_closest_date)
        move_to_closest_date_button.grid(row=1, column=0, padx=10, pady=10)

        previous_all_button = tk.Button(self.additional_frame, text="Previous all", command=self.previous_all)
        previous_all_button.grid(row=2, column=0, padx=10, pady=10)
        
        whitespace = tk.Label(self.additional_frame)
        whitespace.grid(row=3, column=0, padx=10, pady=10)

        settings_button = tk.Button(self.additional_frame, text="Open settings", command=self.open_settings)
        settings_button.grid(row=4, column=0, padx=10, pady=10)
        anchor_button = tk.Button(self.additional_frame, text="Open anchor", command=self.open_anchor)
        anchor_button.grid(row=5, column=0, padx=10, pady=10)
        
        whitespace = tk.Label(self.additional_frame)
        whitespace.grid(row=6, column=0, padx=10, pady=10)

        cam1_button = tk.Button(self.additional_frame, text="Camera 1", command=self.switch_camera_1)
        cam1_button.grid(row=7, column=0, padx=10, pady=10)
        cam2_button = tk.Button(self.additional_frame, text="Camera 2", command=self.switch_camera_2)
        cam2_button.grid(row=8, column=0, padx=10, pady=10)
        cam3_button = tk.Button(self.additional_frame, text="Camera 3", command=self.switch_camera_3)
        cam3_button.grid(row=9, column=0, padx=10, pady=10)
        cam4_button = tk.Button(self.additional_frame, text="Camera 4", command=self.switch_camera_4)
        cam4_button.grid(row=10, column=0, padx=10, pady=10)
        cam5_button = tk.Button(self.additional_frame, text="Camera 5", command=self.switch_camera_5)
        cam5_button.grid(row=11, column=0, padx=10, pady=10)

        # Create a label with arbitrary text
        larger_font = ('Helvetica', 20)  # Change 'Helvetica' to your desired font family and 20 to the desired font size
        self.arbitrary_label = tk.Label(self.root, text=f"Camera {self.current_camera + 1}", font=larger_font)
        self.arbitrary_label.grid(row=0, column=2, padx=10, pady=10)


    def switch_camera_1(self):
        self.current_camera = 0
        self.arbitrary_label.config(text=f"Camera {self.current_camera + 1}")
        self.refresh_images()

    def switch_camera_2(self):
        self.current_camera = 1
        self.arbitrary_label.config(text=f"Camera {self.current_camera + 1}")
        self.refresh_images()

    def switch_camera_3(self):
        self.current_camera = 2
        self.arbitrary_label.config(text=f"Camera {self.current_camera + 1}")
        self.refresh_images()

    def switch_camera_4(self):
        self.current_camera = 3
        self.arbitrary_label.config(text=f"Camera {self.current_camera + 1}")
        self.refresh_images()

    def switch_camera_5(self):
        self.current_camera = 4
        self.arbitrary_label.config(text=f"Camera {self.current_camera + 1}")
        self.refresh_images()

    def create_selectedview_window(self):
        self.selectedview_window = Toplevel(self.root)  # Create a new top-level window
        self.selectedview_window.title("Selected View Window")  # Set the title of the new window

        self.selectedview_frame = tk.Frame(self.selectedview_window)
        self.selectedview_frame.grid(row=SELECTEDVIEW_ROWS, column=SELECTEDVIEW_COLUMNS, columnspan=1)

    def create_settings_window(self):
        self.settings_window = Toplevel(self.root)  # Create a new top-level window
        self.settings_window.title("Settings Window")  # Set the title of the new window

        self.folder_frame = tk.Frame(self.settings_window)
        self.folder_frame.grid(row=0, column=0, columnspan=5)


        for i in range(5):
            folder_label = tk.Label(self.folder_frame, text=f"Folder {i+1}:")
            folder_label.grid(row=0, column=i, padx=10, pady=10)

            folder_path_entry = tk.Entry(self.folder_frame)
            folder_path_entry.grid(row=1, column=i, padx=10, pady=10)
            folder_path_entry.insert(0, self.folder_paths[i])  # Set initial folder path
            folder_path_entry.bind('<FocusOut>', lambda event, index=i: self.update_folder_path(event, index))
            self.folder_path_entries[i] = folder_path_entry  # Update folder_paths list

            browse_button = tk.Button(self.folder_frame, text="Browse", command=lambda i=i: self.browse_folder(i))
            browse_button.grid(row=2, column=i, padx=10, pady=10)

        self.date_cutoff_frame = tk.Frame(self.settings_window)
        self.date_cutoff_frame.grid(row=1, column=1, columnspan=4)

        # Create the Entry widgets for date_cutoff_start and date_cutoff_end
        self.date_cutoff_start_entry = tk.Entry(self.date_cutoff_frame, width=5)
        self.date_cutoff_end_entry = tk.Entry(self.date_cutoff_frame, width=5)
        
        # Create labels next to the Entry widgets
        self.date_cutoff_start_label = tk.Label(self.date_cutoff_frame, text="Start Date:")
        self.date_cutoff_end_label = tk.Label(self.date_cutoff_frame, text="End Date:")
        
        # Add functions to update the variables and print their values
        self.date_cutoff_start_entry.bind("<FocusOut>", self.update_date_cutoff_start)
        self.date_cutoff_end_entry.bind("<FocusOut>", self.update_date_cutoff_end)
        
        # Place the widgets on the GUI
        self.date_cutoff_start_label.grid(row=0, column=0, padx=10, pady=10)
        self.date_cutoff_start_entry.grid(row=0, column=1, padx=10, pady=10)
        self.date_cutoff_end_label.grid(row=0, column=2, padx=10, pady=10)
        self.date_cutoff_end_entry.grid(row=0, column=3, padx=10, pady=10)

    def create_anchor_window(self):
        self.anchor_window = Toplevel(self.root)  # Create a new top-level window
        self.anchor_window.title("Anchor Window")  # Set the title of the new window

        # Create a frame for the anchor image and controls
        self.anchor_frame = tk.Frame(self.anchor_window)
        self.anchor_frame.grid(row=2, column=1, columnspan=3)

        # Add an "Anchor" label
        anchor_label = tk.Label(self.anchor_frame, text="Anchor")
        anchor_label.grid(row=1, column=0, padx=10, pady=10)

        # Add two buttons for the anchor image
        previous_button = tk.Button(self.anchor_frame, text="Previous Anchor", command=self.previous_anchor)
        previous_button.grid(row=0, column=1, padx=10, pady=10)

        next_button = tk.Button(self.anchor_frame, text="Next Anchor", command=self.next_anchor)
        next_button.grid(row=0, column=2, padx=10, pady=10)

        # Add a label for the anchor image name
        self.anchor_image_name_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_name_label.grid(row=0, column=0, columnspan=1)
        # Add a label for the anchor image name
        self.anchor_image_date_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_date_label.grid(row=1, column=1, columnspan=1)

        # Initialize anchor image variables
        
        self.anchor_image_path = ""
        self.anchor_image_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_label.grid(row=1, column=0, columnspan=1, sticky='w')

        # Create buttons to update the anchor image for each column

        self.number_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.number_label.grid(row=1, column=2, padx=10, pady=10)
        larger_font = ('Helvetica', 20)  # Change 'Helvetica' to your desired font family and 20 to the desired font size
        self.number_label.config(font=larger_font)
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()

    def N_show_next_image(self, index):
        for i in range(NUMBER_OF_SKIPS):
            self.show_next_image(index)

    def N_show_previous_image(self, index):
        for i in range(NUMBER_OF_SKIPS):
            self.show_previous_image(index)

    def update_date_cutoff_start(self, event):
        try:
            self.date_cutoff_start = int(self.date_cutoff_start_entry.get())
            print(f"Date Cutoff Start updated to: {self.date_cutoff_start}")
        except ValueError:
            print("Invalid input for Date Cutoff Start. Please enter an integer.")
            self.date_cutoff_start_entry.delete(0, tk.END)
            self.date_cutoff_start_entry.insert(0, str(self.date_cutoff_start))

    def update_date_cutoff_end(self, event):
        try:
            self.date_cutoff_end = int(self.date_cutoff_end_entry.get())
            print(f"Date Cutoff End updated to: {self.date_cutoff_end}")
        except ValueError:
            print("Invalid input for Date Cutoff End. Please enter an integer.")
            self.date_cutoff_end_entry.delete(0, tk.END)
            self.date_cutoff_end_entry.insert(0, str(self.date_cutoff_end))

    def previous_anchor(self):
        if self.current_id < 1:
            return
        self.current_id -= 1
        if str(self.current_id) not in self.image_info:
            self.image_info[str(self.current_id)] = {'image_name':[], 'image_folder':[]}
        self.update_image_click_visualization()
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()

    def next_anchor(self):
        self.current_id += 1
        if str(self.current_id) not in self.image_info:
            self.image_info[str(self.current_id)] = {'image_name':[], 'image_folder':[]}

        self.update_image_click_visualization()
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()  # Load anchor image for the new current_id
    
            
    def next_all(self):
        self.current_image_indices[self.current_camera] += self.clickable_rows*self.clickable_columns
        self.refresh_images()
        self.update_image_click_visualization()

    def open_settings(self):
        try:
            if not self.settings_window.winfo_exists():
                self.create_settings_window()
            else:
                print(f"Settings window already open")
        except:
            self.create_settings_window()

    def open_anchor(self):
        if not self.anchor_window.winfo_exists():
            self.create_anchor_window()
        else:
            print(f"Anchor window already open")

    def move_to_closest_date(self):
        closest = self.find_closest_index(self.image_files_dates[self.current_camera], self.anchor_date)
        N = self.clickable_rows*self.clickable_columns
        closest_rounded = closest - closest % N
        self.current_image_indices[self.current_camera] = closest_rounded
        self.refresh_images()
        self.update_image_click_visualization()

    def previous_all(self):
        self.current_image_indices[self.current_camera] -= 30
        if self.current_image_indices[self.current_camera] < 0:
            self.current_image_indices[self.current_camera] = 0
        self.refresh_images()
        self.update_image_click_visualization()

    def update_number_label_with_value(self, value):
        # Update the number/variable label with the given value
        self.number_label.config(text=str(value))

    def load_anchor_image(self):
        # Load anchor image if it exists for the current_id
        anchor_info = self.anchor_info.get(str(self.current_id))
        anchorset = 0
        if anchor_info:
            folder_name = anchor_info.get("folder_name")
            image_name = anchor_info.get("image_name")
            if folder_name and image_name:
                anchor_image_path = os.path.join(folder_name, image_name)
                if os.path.isfile(anchor_image_path):
                    try:
                        image = Image.open(anchor_image_path)
                        resized_image_with_padding = self.resize_image(image, DESIRED_ANCHOR_WIDTH, DESIRED_ANCHOR_HEIGHT)
                        img = ImageTk.PhotoImage(resized_image_with_padding)
                        self.anchor_image_label.config(image=img)
                        self.anchor_image_label.image = img
                        self.anchor_image_name_label.config(text=image_name)
                        anchor_date = self.extract_date_from_filename(image_name)
                        self.anchor_image_date_label.config(text=anchor_date)
                        self.anchor_date = anchor_date
                        anchorset = 1
                        #print(f"Loading image: {folder_name}, {image_name}")
                    except Exception as e:
                        print(f"Error loading anchor image: {e}")
                else:
                    print("Anchor image not found.")
            else:
                print("Anchor info missing for the current_id.")
            
        if not anchorset:
            white_image = Image.new('RGB', (DESIRED_IMAGE_WIDTH, DESIRED_IMAGE_HEIGHT), 'white')
            white_image_tk = ImageTk.PhotoImage(white_image)

            self.anchor_image_label.config(image=white_image_tk)
            self.anchor_image_label.image = white_image_tk
            self.anchor_image_name_label.config(text="Not set")
            anchor_date = self.anchor_date # last known anchor date
            self.anchor_image_date_label.config(text=anchor_date)
        self.update_selectedview()

    def resize_image(self, image, desired_width, desired_height):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        
        new_width = desired_width
        new_height = int(desired_width / aspect_ratio)

        # Check if the new height exceeds the desired height
        if new_height > new_height:
            new_height = desired_height
            new_width = int(desired_height * aspect_ratio)

        # Calculate the padding on the top and bottom
        padding_top = (desired_height - new_height) // 2
        padding_bottom = desired_height - new_height - padding_top

        # Calculate the padding on the left and right
        padding_left = (desired_width - new_width) // 2
        padding_right = desired_width - new_width - padding_left

        # Resize and add padding to the image
        return ImageOps.expand(image.resize((new_width, new_height)), 
                                                    border=(padding_left, padding_top, padding_right, padding_bottom), 
                                                    fill="black")   

    def update_anchor_from_column(self, n):
        current_index = self.current_image_indices[self.current_camera]+n
        folder_path = self.folder_paths[self.current_camera]
        image_name = self.image_files_list[self.current_camera][current_index]
        anchor_image_path = os.path.join(folder_path, image_name)
        if os.path.isfile(anchor_image_path):
            try:
                # Update anchor info with the anchor image name and folder name for the current ID
                anchor_info = self.anchor_info
                anchor_info[str(self.current_id)] = {"image_name": image_name, "folder_name": folder_path}
                self.save_anchor_info()
                self.load_anchor_image()

                print(f"Loading image: {folder_path}, {image_name}")
            except Exception as e:
                print(f"Error loading anchor image: {e}")
        else:
                print(f"Anchor image not found for column {column_index + 1}.")


    def browse_folder(self, index):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_entries[index].delete(0, tk.END)  # Clear Entry widget
            self.folder_path_entries[index].insert(0, folder_path)  # Update Entry widget
            self.folder_paths[index] = folder_path
            self.load_image(index, folder_path)

    def update_folder_path(self, event, index):
        folder_path = self.folder_paths[index]  # Get the text from the Entry widget
        folder_path = folder_path.replace('/', '\\')  # Correct path format for Windows
        folder_path = os.path.normpath(folder_path)  # Normalize path
        self.folder_path_entries[index].delete(0, tk.END)  # Clear Entry widget
        self.folder_path_entries[index].insert(0, folder_path)  # Update Entry widget
        self.folder_paths[index] = folder_path
        self.load_image(index, folder_path)

    def refresh_images(self):
        for i in range(self.clickable_rows):
            for j in range(self.clickable_columns):
                if os.path.isdir(self.folder_paths[self.current_camera]):
                    n = j+i*self.clickable_rows
                    self.show_image(self.current_camera, self.folder_paths[self.current_camera], n)

    def reload_all_images(self):
        for i, folder_path in enumerate(self.folder_paths):
            if os.path.isdir(folder_path):
                self.load_image(i, folder_path)
            else:
                print(f"Error, not a dir: {folder_path} - {self.folder_paths}")

    def find_closest_index(self, numbers_string_list, target_string):
        if not numbers_string_list:
            return None  # Handle an empty list if neededcl
        try:
            numbers = [int(numbers_string) for numbers_string in numbers_string_list]
            target = int(target_string)
        except Exception as e:
            print(f"Date invalid: {e}")
            return 0

        closest_index = 0  # Initialize with the first index
        closest_difference = abs(numbers[0] - target)  # Initialize with the difference to the first element
        
        for i in range(1, len(numbers)):
            difference = abs(numbers[i] - target)
            if difference < closest_difference:
                closest_index = i
                closest_difference = difference

        return closest_index

    def load_image(self, index, folder_path):
        try:
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
            image_files_dates = [self.extract_date_from_filename(filename) for filename in image_files]
            if image_files:
                pairs = list(zip(image_files_dates, image_files))
                sorted_pairs = sorted(pairs, key=lambda x: x[0])
                self.image_files_list[index] = [pair[1] for pair in sorted_pairs]
                self.image_files_dates[index] = [pair[0] for pair in sorted_pairs]
                print(pairs)
                print(sorted_pairs)
            else:
                print("No .jpg files found in the selected folder.")
        except Exception as e:
            print(f"Error loading image: {e}")

    def extract_and_update_date(self, filename, n):
        try:
            output_date_string = ""
            date_string = self.extract_date_from_filename(filename)
            for i in range(0, len(date_string), 2):
                output_date_string += date_string[i:i+2] + ":"
            output_date_string = output_date_string[:-1]
            self.date_labels[n].config(text=output_date_string)
        except:
            print(f"Cannot cut [{self.date_cutoff_start}, {self.date_cutoff_end}] from text: {filename}")

    def show_image(self, index, folder_path, n):
        try:
            image_index = self.current_image_indices[self.current_camera] + n
            image_file = os.path.join(folder_path, self.image_files_list[index][image_index])
            image = Image.open(image_file)
            # Calculate the width based on the desired height and the original aspect ratio
            
            resized_image_with_padding = self.resize_image(image, DESIRED_IMAGE_WIDTH, DESIRED_IMAGE_HEIGHT)

            img = ImageTk.PhotoImage(resized_image_with_padding)
            
            truncated_filename = self.truncate_filename(self.image_files_list[index][image_index])
            
            self.extract_and_update_date(self.image_files_list[index][image_index], n)

            self.image_labels[n].config(image=img, text=self.image_files_list[index][image_index])
            self.image_labels[n].image = img

            # Update image click visualization
            self.update_image_click_visualization()
        except Exception as e:
            #print(f"Error loading image 2: {e}")
            white_image = Image.new('RGB', (DESIRED_IMAGE_WIDTH, DESIRED_IMAGE_HEIGHT), 'white')
            white_image_tk = ImageTk.PhotoImage(white_image)

            self.image_labels[n].config(image=white_image_tk, text="-")
            self.image_labels[n].image = white_image_tk

    def truncate_filename(self, filename):
        if len(filename) > MAX_FILENAME_LENGTH:
                # Truncate the file name to fit within the limit
            truncated_filename = filename[:MAX_FILENAME_LENGTH - 3]
        else:
            truncated_filename = filename

    def extract_date_from_filename(self, filename):
        return filename[-self.date_cutoff_start:-self.date_cutoff_end]
        

    def toggle_image_click(self, index):
        if hasattr(self, 'image_files_list') and hasattr(self, 'image_info'):
            # Toggle the click status for the current image in its corresponding folder
            image_name = self.image_files_list[self.current_camera][self.current_image_indices[self.current_camera] + index]
            folder_name = self.folder_paths[self.current_camera]
            image_info = self.image_info[str(self.current_id)]

            in_set = 0
            if image_name in image_info['image_name']:
                image_indexes = [index for index, value in enumerate(image_info['image_name']) if value == image_name]
                for image_index in image_indexes:
                    if folder_name == image_info['image_folder'][image_index]:
                        in_set = 1
                        break

            if in_set:
                image_info['image_name'].pop(image_index)
                image_info['image_folder'].pop(image_index)
            else:
                image_info['image_name'].append(image_name)
                image_info['image_folder'].append(folder_name)


            # Update image click visualization
            self.update_image_click_visualization()
        self.update_selectedview()

    def show_next_image(self, index):
        if hasattr(self, 'image_files_list'):
            self.current_image_indices[index] = (self.current_image_indices[index] + 1) % len(self.image_files_list[index])
            self.show_image(index, self.folder_paths[index], self.current_image_indices[index])

    def show_previous_image(self, index):
        if hasattr(self, 'image_files_list'):
            self.current_image_indices[index] = (self.current_image_indices[index] - 1) % len(self.image_files_list[index])
            self.show_image(index, self.folder_paths[index], self.current_image_indices[index])

    def update_image_click_visualization(self):
        for i, image_label in enumerate(self.image_labels):
            if hasattr(self, 'image_files_list') and hasattr(self, 'image_info'):
                self.image_frames[i].config(bg="grey")
                current_index = self.current_image_indices[self.current_camera] + i
                if not self.image_files_list[self.current_camera]:
                    continue
                if len(self.image_files_list[self.current_camera]) <= current_index:
                    continue
                image_name = self.image_files_list[self.current_camera][current_index]

                # Check if the stored value matches the current_id
                folder_name = self.folder_paths[self.current_camera]
                image_info = self.image_info[str(self.current_id)]
                click_status = False
                if image_name in image_info['image_name']:
                    image_indexes = [index for index, value in enumerate(image_info['image_name']) if value == image_name]
                    for image_index in image_indexes:
                        if folder_name == image_info['image_folder'][image_index]:
                            click_status = True
                            break

                # Update the background color of the image frame to visualize the click status
                background_color = "green" if click_status else "red"
                self.image_frames[i].config(bg=background_color)
        
    def update_selectedview(self):
        for image_label in self.selectedviewimages_list:
            image_label.destroy()
        image_info = self.image_info[str(self.current_id)]
        for i, [image_name, image_path] in enumerate(zip(image_info['image_name'], image_info['image_folder'])):
            image_path = f"{image_path}/{image_name}"
            self.load_and_display_image_selectedview(image_path, i)

    def load_and_display_image_selectedview(self, image_path, i):
        try:
            row = i // SELECTEDVIEW_COLUMNS
            column = i % SELECTEDVIEW_COLUMNS
            image = Image.open(image_path)
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            
            new_width = DESIRED_SELECTVIEW_WIDTH
            new_height = int(DESIRED_SELECTVIEW_WIDTH / aspect_ratio)

            # Check if the new height exceeds the desired height
            if new_height > new_height:
                new_height = DESIRED_SELECTVIEW_HEIGHT
                new_width = int(DESIRED_SELECTVIEW_HEIGHT * aspect_ratio)

            # Calculate the padding on the top and bottom
            padding_top = (DESIRED_SELECTVIEW_HEIGHT - new_height) // 2
            padding_bottom = DESIRED_SELECTVIEW_HEIGHT - new_height - padding_top

            # Calculate the padding on the left and right
            padding_left = (DESIRED_SELECTVIEW_WIDTH - new_width) // 2
            padding_right = DESIRED_SELECTVIEW_WIDTH - new_width - padding_left

            # Resize and add padding to the image
            resized_image_with_padding = ImageOps.expand(image.resize((new_width, new_height)), 
                                                        border=(padding_left, padding_top, padding_right, padding_bottom), 
                                                        fill="black")
            photo = ImageTk.PhotoImage(resized_image_with_padding)
            label = tk.Label(self.selectedview_frame, image=photo)
            
            label.image = photo
            label.grid(row=row, column=column, columnspan=1, sticky='w')
            self.selectedviewimages_list.append(label)
        except Exception as e:
            print(f"Cannot load image 3: {e}")

    def load_image_info(self):
        try:
            # Load image info (click status and folder name for each column) from a JSON file
            with open("image_info.json", "r") as json_file:
                self.image_info = json.load(json_file)
        except FileNotFoundError:
            # Initialize image info with default values if the file doesn't exist
            self.image_info = {str(self.current_id):{'image_name':[], 'image_folder':[]}}

    def save_image_info(self):
        # Save image info (click status and folder name for each column) to a JSON file
        with open("image_info.json", "w") as json_file:
            json.dump(self.image_info, json_file)

    def load_anchor_info(self):
        try:
            # Load anchor info (anchor image name and folder name for each current_id) from a JSON file
            with open("anchor_info.json", "r") as json_file:
                self.anchor_info = json.load(json_file)
        except FileNotFoundError:
            # Initialize anchor info with default values if the file doesn't exist
            self.anchor_info = {}
            
    def save_anchor_info(self):
        # Save anchor info (anchor image name and folder name for each current_id) to a JSON file
        with open("anchor_info.json", "w") as json_file:
            json.dump(self.anchor_info, json_file)

    def load_settings(self):
        try:
            # Load settings from settings.json
            with open("settings.json", "r") as json_file:
                settings_data = json.load(json_file)
                self.folder_paths = settings_data.get("folder_paths", [""] * 5)
                self.current_id = settings_data.get("current_id", 0)
                self.current_image_indices = settings_data.get("current_image_indices", [0] * 5)
                print(f"Loaded settings: {self.folder_paths}, {self.current_id}, {self.current_image_indices}")
        except FileNotFoundError:
            # Initialize folder paths with empty strings, current_id with 0, and current_image_indices with 0 for all columns
            self.folder_paths = [""] * 5
            self.current_id = 0
            self.current_image_indices = [0] * 5

    def save_settings(self):
        # Save folder paths, current_id, and current_image_indices to settings.json
        settings_data = {
            "folder_paths": self.folder_paths,
            "current_id": self.current_id,
            "current_image_indices": self.current_image_indices
        }
        with open("settings.json", "w") as json_file:
            json.dump(settings_data, json_file)

    def save_settings_and_image_info(self):
        self.save_settings()
        self.save_image_info()
        self.save_anchor_info()
        self.root.destroy()


if __name__ == "__main__":
    app = tk.Tk()
    viewer = ImageViewer(app)
    app.protocol("WM_DELETE_WINDOW", viewer.save_settings_and_image_info)  # Save settings and image info on window close
    app.mainloop()
