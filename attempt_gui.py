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
NUMBER_OF_SKIPS = 5

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
        self.image_names = []  # List to store image names
        self.image_info = {}  # dict to store image info (click status and folder name for each column)
        self.anchor_info = []  # List to store anchor info (anchor image name and folder name for each current_id)
        self.image_files_list = []  # List to store image files for each column
        self.current_image_indices = [0, 0, 0, 0, 0]  # Separate current image indices for each column
        self.current_id = 0
        # Set initial values for date_cutoff_start and date_cutoff_end
        self.date_cutoff_start = 10
        self.date_cutoff_end = 4

        # Load or initialize the image info data from a JSON file
        self.load_settings()
        self.load_image_info()
        self.load_anchor_info()

        # @@@ Settings
        self.create_settings_window()
        for i in range(5):
            image_frame = tk.Frame(self.root)
            image_frame.grid(row=4, column=i, padx=10, pady=10)
            self.image_frames.append(image_frame)

            N_top_button = tk.Button(image_frame, text=f"{NUMBER_OF_SKIPS}x Next", state=tk.DISABLED, command=lambda i=i: self.N_show_next_image(i))
            N_top_button.pack()
            top_button = tk.Button(image_frame, text="Next image", state=tk.DISABLED, command=lambda i=i: self.show_next_image(i))
            top_button.pack()
            self.top_buttons.append(top_button)
            self.N_top_buttons.append(N_top_button)

            image_label = tk.Label(image_frame, text="", padx=10, pady=10)
            image_label.pack()
            image_label.bind("<Button-1>", lambda event, index=i: self.toggle_image_click(index))
            self.image_labels.append(image_label)

            bottom_button = tk.Button(image_frame, text="Previous Image", state=tk.DISABLED, command=lambda i=i: self.show_previous_image(i))
            bottom_button.pack()
            N_bottom_button = tk.Button(image_frame, text=f"{NUMBER_OF_SKIPS}x Previous", state=tk.DISABLED, command=lambda i=i: self.N_show_previous_image(i))
            N_bottom_button.pack()
            self.bottom_buttons.append(bottom_button)
            self.N_bottom_buttons.append(N_bottom_button)

            image_name_label = tk.Label(image_frame, text="", padx=10)
            image_name_label.pack()
            self.image_names.append(image_name_label)

            # Initialize an empty list for image files
            self.image_files_list.append([])
        # Update image clicks and borders to visualize
        self.reload_all_images()
        self.update_image_click_visualization()

        # @@@ Anchor
        self.create_anchor_window()

        # @@@ Buttons
        self.additional_frame = tk.Frame(self.root)
        self.additional_frame.grid(row=0, column=5, rowspan=9, padx=10, pady=10)

        # Create buttons in the new column
        button1 = tk.Button(self.additional_frame, text="Next all", command=self.next_all)
        button1.grid(row=0, column=0, padx=10, pady=10)

        button2 = tk.Button(self.additional_frame, text="Button 2", command=self.print_message2)
        button2.grid(row=1, column=0, padx=10, pady=10)

        button3 = tk.Button(self.additional_frame, text="Previous all", command=self.previous_all)
        button3.grid(row=2, column=0, padx=10, pady=10)
        
        whitespace = tk.Label(self.additional_frame)
        whitespace.grid(row=3, column=0, padx=10, pady=10)

        settings_button = tk.Button(self.additional_frame, text="Open settings", command=self.open_settings)
        settings_button.grid(row=4, column=0, padx=10, pady=10)
        anchor_button = tk.Button(self.additional_frame, text="Open anchor", command=self.open_anchor)
        anchor_button.grid(row=5, column=0, padx=10, pady=10)


        self.date_labels = []  # List to store date labels

        for i in range(5):
            # Create a label with an arbitrary date (you can replace it later)
            date_label = tk.Label(self.root, text="Arbitrary Date", padx=10, pady=10)
            date_label.grid(row=3, column=i)
            self.date_labels.append(date_label)

        # Create a label with arbitrary text
        self.arbitrary_label = tk.Label(self.root, text="Arbitrary Text")
        self.arbitrary_label.grid(row=0, column=2, padx=10, pady=10)


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
        anchor_label.grid(row=0, column=0, padx=10, pady=10)

        # Add two buttons for the anchor image
        previous_button = tk.Button(self.anchor_frame, text="Previous Anchor", command=self.previous_anchor)
        previous_button.grid(row=0, column=1, padx=10, pady=10)

        next_button = tk.Button(self.anchor_frame, text="Next Anchor", command=self.next_anchor)
        next_button.grid(row=0, column=2, padx=10, pady=10)

        # Add a label for the anchor image name
        self.anchor_image_name_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_name_label.grid(row=1, column=3, columnspan=1)

        # Initialize anchor image variables
        self.anchor_image = None
        self.anchor_image_path = ""
        self.anchor_image_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_label.grid(row=1, column=2, columnspan=1, sticky='w')

        # Create buttons to update the anchor image for each column
        self.update_anchor_buttons = []
        for i in range(5):
            update_anchor_button = tk.Button(self.root, text=f"Update Anchor {i+1}", command=lambda i=i: self.update_anchor_from_column(i))
            update_anchor_button.grid(row=5, column=i, padx=10, pady=10)
            self.update_anchor_buttons.append(update_anchor_button)

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
        if self.anchor_info.get(str(self.current_id)) is None:
            # No new anchor found, remove the anchor image
            self.clear_anchor_image()  

    def next_anchor(self):
        self.current_id += 1
        if str(self.current_id) not in self.image_info:
            self.image_info[str(self.current_id)] = {'image_name':[], 'image_folder':[]}

        self.update_image_click_visualization()
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()  # Load anchor image for the new current_id

        # Check if there is an anchor image for the new current_id
        if self.anchor_info.get(str(self.current_id)) is None:
            print(f"No anchor found")
            # No new anchor found, remove the anchor image
            self.clear_anchor_image()
            
    def next_all(self):
        for index in range(5):
            self.show_next_image(index)

    def open_settings(self):
        if not self.settings_window.winfo_exists():
            self.create_settings_window()
        else:
            print(f"Settings window already open")

    def open_anchor(self):
        if not self.anchor_window.winfo_exists():
            self.create_anchor_window()
        else:
            print(f"Anchor window already open")

    def print_message2(self):
        pass

    def previous_all(self):
        for index in range(5):
            self.show_previous_image(index)

    def update_number_label_with_value(self, value):
        # Update the number/variable label with the given value
        self.number_label.config(text=str(value))

    def load_anchor_image(self):
        # Load anchor image if it exists for the current_id
        anchor_info = self.anchor_info.get(str(self.current_id))
        if anchor_info:
            folder_name = anchor_info.get("folder_name")
            image_name = anchor_info.get("image_name")
            if folder_name and image_name:
                anchor_image_path = os.path.join(folder_name, image_name)
                if os.path.isfile(anchor_image_path):
                    try:
                        image = Image.open(anchor_image_path)
                        original_width, original_height = image.size
                        aspect_ratio = original_width / original_height
                        
                        new_width = DESIRED_ANCHOR_WIDTH
                        new_height = int(DESIRED_ANCHOR_WIDTH / aspect_ratio)

                        # Check if the new height exceeds the desired height
                        if new_height > new_height:
                            new_height = DESIRED_ANCHOR_HEIGHT
                            new_width = int(DESIRED_ANCHOR_HEIGHT * aspect_ratio)

                        # Calculate the padding on the top and bottom
                        padding_top = (DESIRED_ANCHOR_HEIGHT - new_height) // 2
                        padding_bottom = DESIRED_ANCHOR_HEIGHT - new_height - padding_top

                        # Calculate the padding on the left and right
                        padding_left = (DESIRED_ANCHOR_WIDTH - new_width) // 2
                        padding_right = DESIRED_ANCHOR_WIDTH - new_width - padding_left

                        # Resize and add padding to the image
                        resized_image_with_padding = ImageOps.expand(image.resize((new_width, new_height)), 
                                                                    border=(padding_left, padding_top, padding_right, padding_bottom), 
                                                                    fill="black")
                        img = ImageTk.PhotoImage(resized_image_with_padding)
                        self.anchor_image_label.config(image=img)
                        self.anchor_image_label.image = img
                        self.anchor_image = img
                        self.anchor_image_name_label.config(text=image_name)
                        print(f"Loading image: {folder_name}, {image_name}")
                    except Exception as e:
                        print(f"Error loading anchor image: {e}")
                else:
                    print("Anchor image not found.")
            else:
                print("Anchor info missing for the current_id.")

    def update_anchor_from_column(self, column_index):
        folder_path = self.folder_paths[column_index]
        current_index = self.current_image_indices[column_index]
        if current_index < len(self.image_files_list[column_index]):
            image_name = self.image_files_list[column_index][current_index]
            anchor_image_path = os.path.join(folder_path, image_name)
            if os.path.isfile(anchor_image_path):
                try:
                    # Update anchor info with the anchor image name and folder name for the current ID
                    anchor_info = self.anchor_info
                    anchor_info[str(self.current_id)] = {"image_name": image_name, "folder_name": folder_path}
                    self.save_anchor_info()

                    image = Image.open(anchor_image_path)
                    original_width, original_height = image.size
                    aspect_ratio = original_width / original_height
                    
                    new_width = DESIRED_ANCHOR_WIDTH
                    new_height = int(DESIRED_ANCHOR_WIDTH / aspect_ratio)

                    # Check if the new height exceeds the desired height
                    if new_height > new_height:
                        new_height = DESIRED_ANCHOR_HEIGHT
                        new_width = int(DESIRED_ANCHOR_HEIGHT * aspect_ratio)

                    # Calculate the padding on the top and bottom
                    padding_top = (DESIRED_ANCHOR_HEIGHT - new_height) // 2
                    padding_bottom = DESIRED_ANCHOR_HEIGHT - new_height - padding_top

                    # Calculate the padding on the left and right
                    padding_left = (DESIRED_ANCHOR_WIDTH - new_width) // 2
                    padding_right = DESIRED_ANCHOR_WIDTH - new_width - padding_left

                    # Resize and add padding to the image
                    resized_image_with_padding = ImageOps.expand(image.resize((new_width, new_height)), 
                                                                border=(padding_left, padding_top, padding_right, padding_bottom), 
                                                                fill="black")
                    img = ImageTk.PhotoImage(resized_image_with_padding)
                    self.anchor_image_label.config(image=img)
                    self.anchor_image_label.image = img
                    self.anchor_image = img
                    self.anchor_image_name_label.config(text=image_name)
                    print(f"Loading image: {folder_path}, {image_name}")
                except Exception as e:
                    print(f"Error loading anchor image: {e}")
            else:
                print(f"Anchor image not found for column {column_index + 1}.")

    def clear_anchor_image(self):
        self.anchor_image_label.destroy()
        self.anchor_image_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_label.grid(row=1, column=0, columnspan=3, sticky='w')
        self.anchor_image = None
        self.anchor_image_path = ""
        self.anchor_image_name_label.config(text="")

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

    def reload_all_images(self):
        for i, folder_path in enumerate(self.folder_paths):
            if os.path.isdir(folder_path):
                self.load_image(i, folder_path)
            else:
                print(f"Error, not a dir: {folder_path} - {self.folder_paths}")

    def load_image(self, index, folder_path):
        try:
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
            image_files_dates = [name[-self.date_cutoff_start:-self.date_cutoff_end] for name in image_files]
            if image_files:
                self.image_files_list[index] = image_files
                #self.current_image_indices[index] = 0
                self.show_image(index, folder_path, self.current_image_indices[index])
            else:
                print("No .jpg files found in the selected folder.")
        except Exception as e:
            print(f"Error loading image: {e}")

    def extract_and_update_date(self, filename, index):
        try:
            output_date_string = ""
            date_string = filename[-self.date_cutoff_start:-self.date_cutoff_end]
            for i in range(0, len(date_string), 2):
                output_date_string += date_string[i:i+2] + ":"
            output_date_string = output_date_string[:-1]
            self.date_labels[index].config(text=output_date_string)
            print(f"Cutoff from {filename} to {output_date_string}")
        except:
            print(f"Cannot cut [{self.date_cutoff_start}, {self.date_cutoff_end}] from text: {filename}")

    def show_image(self, index, folder_path, image_index):
        try:
            image_file = os.path.join(folder_path, self.image_files_list[index][image_index])
            image = Image.open(image_file)
            # Calculate the width based on the desired height and the original aspect ratio
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            
            new_width = DESIRED_IMAGE_WIDTH
            new_height = int(DESIRED_IMAGE_WIDTH / aspect_ratio)

            # Check if the new height exceeds the desired height
            if new_height > new_height:
                new_height = DESIRED_IMAGE_HEIGHT
                new_width = int(DESIRED_IMAGE_HEIGHT * aspect_ratio)

            # Calculate the padding on the top and bottom
            padding_top = (DESIRED_IMAGE_HEIGHT - new_height) // 2
            padding_bottom = DESIRED_IMAGE_HEIGHT - new_height - padding_top

            # Calculate the padding on the left and right
            padding_left = (DESIRED_IMAGE_WIDTH - new_width) // 2
            padding_right = DESIRED_IMAGE_WIDTH - new_width - padding_left

            # Resize and add padding to the image
            resized_image_with_padding = ImageOps.expand(image.resize((new_width, new_height)), 
                                                        border=(padding_left, padding_top, padding_right, padding_bottom), 
                                                        fill="black")

            # Resize the image to the calculated width and desired height
            image = image.resize((new_width, DESIRED_IMAGE_HEIGHT))
            img = ImageTk.PhotoImage(resized_image_with_padding)
            
            if len(self.image_files_list[index][image_index]) > MAX_FILENAME_LENGTH:
                # Truncate the file name to fit within the limit
                truncated_filename = self.image_files_list[index][image_index][:MAX_FILENAME_LENGTH - 3] + "..."
            else:
                truncated_filename = self.image_files_list[index][image_index]
            
            self.extract_and_update_date(self.image_files_list[index][image_index], index)

            self.image_labels[index].config(image=img, text=self.image_files_list[index][image_index])
            self.image_labels[index].image = img
            #self.image_names[index].config(text=truncated_filename)  # Display image name
            self.image_names[index].config(text=f"{self.current_image_indices[index]}")  # Display image name
            self.top_buttons[index].config(state=tk.NORMAL)
            self.N_top_buttons[index].config(state=tk.NORMAL)
            self.bottom_buttons[index].config(state=tk.NORMAL)
            self.N_bottom_buttons[index].config(state=tk.NORMAL)

            # Update image click visualization
            self.update_image_click_visualization()
        except Exception as e:
            print(f"Error loading image: {e}")

    def toggle_image_click(self, index):
        if hasattr(self, 'image_files_list') and hasattr(self, 'image_info'):
            # Toggle the click status for the current image in its corresponding folder
            image_name = self.image_files_list[index][self.current_image_indices[index]]
            folder_name = self.folder_paths[index]
            image_info = self.image_info[str(self.current_id)]

            in_set = 0
            if image_name in image_info['image_name']:
                image_index = image_info['image_name'].index(image_name)
                if folder_name == image_info['image_folder'][image_index]:
                    in_set = 1

            if in_set:
                image_info['image_name'].pop(image_index)
                image_info['image_folder'].pop(image_index)
            else:
                image_info['image_name'].append(image_name)
                image_info['image_folder'].append(folder_name)


            # Update image click visualization
            self.update_image_click_visualization()

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
                current_index = self.current_image_indices[i]

                if current_index < len(self.image_files_list[i]):
                    image_name = self.image_files_list[i][current_index]

                    # Check if the stored value matches the current_id
                    folder_name = self.folder_paths[i]
                    image_info = self.image_info[str(self.current_id)]
                    click_status = False
                    if image_name in image_info['image_name']:
                        image_index = image_info['image_name'].index(image_name)
                        if folder_name == image_info['image_folder'][image_index]:
                            click_status = True

                    # Update the background color of the image frame to visualize the click status
                    background_color = "green" if click_status else "red"
                    self.image_frames[i].config(bg=background_color)

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
