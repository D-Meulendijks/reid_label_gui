import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json

MAX_FILENAME_LENGTH = 8
DESIRED_IMAGE_HEIGHT = 200

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")

        self.folder_paths = [""] * 5  # Initialize with 5 empty Entry widgets
        self.image_frames = []
        self.image_labels = []
        self.top_buttons = []
        self.bottom_buttons = []
        self.image_names = []  # List to store image names
        self.image_info = []  # List to store image info (click status and folder name for each column)
        self.anchor_info = []  # List to store anchor info (anchor image name and folder name for each current_id)
        self.image_files_list = []  # List to store image files for each column
        self.current_image_indices = [0, 0, 0, 0, 0]  # Separate current image indices for each column
        self.current_id = 0

        # Load or initialize the image info data from a JSON file
        self.load_image_info()
        self.load_anchor_info()
        self.load_settings()

        self.folder_frame = tk.Frame(self.root)
        self.folder_frame.grid(row=8, column=0, columnspan=5)

        for i in range(5):
            folder_label = tk.Label(self.folder_frame, text=f"Folder {i+1}:")
            folder_label.grid(row=0, column=i, padx=10, pady=10)

            folder_path_entry = tk.Entry(self.folder_frame)
            folder_path_entry.grid(row=1, column=i, padx=10, pady=10)
            folder_path_entry.insert(0, self.folder_paths[i])  # Set initial folder path
            folder_path_entry.bind('<FocusOut>', lambda event, index=i: self.update_folder_path(event, index))
            self.folder_paths[i] = folder_path_entry  # Update folder_paths list

            browse_button = tk.Button(self.folder_frame, text="Browse", command=lambda i=i: self.browse_folder(i))
            browse_button.grid(row=2, column=i, padx=10, pady=10)

        for i in range(5):
            image_frame = tk.Frame(self.root)
            image_frame.grid(row=4, column=i, padx=10, pady=10)
            self.image_frames.append(image_frame)

            top_button = tk.Button(image_frame, text="Top Button", state=tk.DISABLED, command=lambda i=i: self.show_next_image(i))
            top_button.pack()
            self.top_buttons.append(top_button)

            image_label = tk.Label(image_frame, text="", padx=10, pady=10)
            image_label.pack()
            image_label.bind("<Button-1>", lambda event, index=i: self.toggle_image_click(index))
            self.image_labels.append(image_label)

            bottom_button = tk.Button(image_frame, text="Bottom Button", state=tk.DISABLED, command=lambda i=i: self.show_previous_image(i))
            bottom_button.pack()
            self.bottom_buttons.append(bottom_button)

            image_name_label = tk.Label(image_frame, text="", padx=10)
            image_name_label.pack()
            self.image_names.append(image_name_label)

            # Initialize an empty list for image files
            self.image_files_list.append([])

        # Update image clicks and borders to visualize
        self.reload_all_images()
        self.update_image_click_visualization()

        # Create a frame for the anchor image and controls
        self.anchor_frame = tk.Frame(self.root)
        self.anchor_frame.grid(row=0, column=0, columnspan=5)

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
        self.anchor_image_name_label.grid(row=1, column=0, columnspan=3)

        # Initialize anchor image variables
        self.anchor_image = None
        self.anchor_image_path = ""
        self.anchor_image_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.anchor_image_label.grid(row=1, column=0, columnspan=3, sticky='w')

        # Create buttons to update the anchor image for each column
        self.update_anchor_buttons = []
        for i in range(5):
            update_anchor_button = tk.Button(self.root, text=f"Update Anchor {i+1}", command=lambda i=i: self.update_anchor_from_column(i))
            update_anchor_button.grid(row=5, column=i, padx=10, pady=10)
            self.update_anchor_buttons.append(update_anchor_button)

        self.additional_frame = tk.Frame(self.root)
        self.additional_frame.grid(row=0, column=5, rowspan=9, padx=10, pady=10)

        # Create buttons in the new column
        button1 = tk.Button(self.additional_frame, text="Button 1", command=self.print_message1)
        button1.grid(row=0, column=0, padx=10, pady=10)

        button2 = tk.Button(self.additional_frame, text="Button 2", command=self.print_message2)
        button2.grid(row=1, column=0, padx=10, pady=10)

        button3 = tk.Button(self.additional_frame, text="Button 3", command=self.print_message3)
        button3.grid(row=2, column=0, padx=10, pady=10)

        self.number_label = tk.Label(self.anchor_frame, text="", padx=10)
        self.number_label.grid(row=1, column=2, padx=10, pady=10)
        larger_font = ('Helvetica', 20)  # Change 'Helvetica' to your desired font family and 20 to the desired font size
        self.number_label.config(font=larger_font)
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()

    def previous_anchor(self):
        if self.current_id < 1:
            return
        self.current_id -= 1
        self.update_image_click_visualization()
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()
        if self.anchor_info.get(str(self.current_id)) is None:
            # No new anchor found, remove the anchor image
            self.clear_anchor_image()

    def next_anchor(self):
        self.current_id += 1
        self.update_image_click_visualization()
        self.update_number_label_with_value(self.current_id)
        self.load_anchor_image()  # Load anchor image for the new current_id

        # Check if there is an anchor image for the new current_id
        if self.anchor_info.get(str(self.current_id)) is None:
            print(f"No anchor found")
            # No new anchor found, remove the anchor image
            self.clear_anchor_image()

    def print_message1(self):
        print("Button 1 clicked")

    def print_message2(self):
        print("Button 2 clicked")

    def print_message3(self):
        print("Button 3 clicked")

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
                        image.thumbnail((100, 100))
                        img = ImageTk.PhotoImage(image)
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
        folder_path = self.folder_paths[column_index].get()
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
                    image.thumbnail((100, 100))
                    img = ImageTk.PhotoImage(image)
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
            self.folder_paths[index].delete(0, tk.END)  # Clear Entry widget
            self.folder_paths[index].insert(0, folder_path)  # Update Entry widget
            self.load_image(index, folder_path)

    def update_folder_path(self, event, index):
        folder_path = self.folder_paths[index].get()  # Get the text from the Entry widget
        folder_path = folder_path.replace('/', '\\')  # Correct path format for Windows
        folder_path = os.path.normpath(folder_path)  # Normalize path
        self.folder_paths[index].delete(0, tk.END)  # Clear Entry widget
        self.folder_paths[index].insert(0, folder_path)  # Update Entry widget
        self.load_image(index, folder_path)

    def reload_all_images(self):
        for i, folder_path in enumerate(self.folder_paths):
            if os.path.isdir(folder_path.get()):
                self.load_image(i, folder_path.get())
            else:
                print(f"Error, not a dir: {folder_path.get()}")

    def load_image(self, index, folder_path):
        try:
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
            if image_files:
                self.image_files_list[index] = image_files
                #self.current_image_indices[index] = 0
                self.show_image(index, folder_path, self.current_image_indices[index])
            else:
                print("No .jpg files found in the selected folder.")
        except Exception as e:
            print(f"Error loading image: {e}")

    def show_image(self, index, folder_path, image_index):
        try:
            image_file = os.path.join(folder_path, self.image_files_list[index][image_index])
            image = Image.open(image_file)
            # Calculate the width based on the desired height and the original aspect ratio
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            new_width = int(DESIRED_IMAGE_HEIGHT * aspect_ratio)

            # Resize the image to the calculated width and desired height
            image.thumbnail((new_width, DESIRED_IMAGE_HEIGHT))
            img = ImageTk.PhotoImage(image)
            
            if len(self.image_files_list[index][image_index]) > MAX_FILENAME_LENGTH:
                # Truncate the file name to fit within the limit
                truncated_filename = self.image_files_list[index][image_index][:MAX_FILENAME_LENGTH - 3] + "..."
            else:
                truncated_filename = self.image_files_list[index][image_index]
            self.image_labels[index].config(image=img, text=self.image_files_list[index][image_index])
            self.image_labels[index].image = img
            self.image_names[index].config(text=truncated_filename)  # Display image name
            self.top_buttons[index].config(state=tk.NORMAL)
            self.bottom_buttons[index].config(state=tk.NORMAL)

            # Update image click visualization
            self.update_image_click_visualization()
        except Exception as e:
            print(f"Error loading image: {e}")

    def toggle_image_click(self, index):
        if hasattr(self, 'image_files_list') and hasattr(self, 'image_info'):
            # Toggle the click status for the current image in its corresponding folder
            image_name = self.image_files_list[index][self.current_image_indices[index]]
            folder_name = self.folder_paths[index]
            image_info = self.image_info[index]

            if image_name in image_info:
                # Check if the current_id matches the stored value
                if image_info[image_name] == self.current_id:
                    del image_info[image_name]  # Remove the entry to switch back to default (red)
                else:
                    image_info[image_name] = self.current_id
            else:
                image_info[image_name] = self.current_id

            # Update image click visualization
            self.update_image_click_visualization()

    def show_next_image(self, index):
        if hasattr(self, 'image_files_list'):
            self.current_image_indices[index] = (self.current_image_indices[index] + 1) % len(self.image_files_list[index])
            self.show_image(index, self.folder_paths[index].get(), self.current_image_indices[index])

    def show_previous_image(self, index):
        if hasattr(self, 'image_files_list'):
            self.current_image_indices[index] = (self.current_image_indices[index] - 1) % len(self.image_files_list[index])
            self.show_image(index, self.folder_paths[index].get(), self.current_image_indices[index])

    def update_image_click_visualization(self):
        for i, image_label in enumerate(self.image_labels):
            if hasattr(self, 'image_files_list') and hasattr(self, 'image_info'):
                folder_name = self.folder_paths[i]
                image_info = self.image_info[i]
                current_index = self.current_image_indices[i]

                if current_index < len(self.image_files_list[i]):
                    image_name = self.image_files_list[i][current_index]

                    # Check if the stored value matches the current_id
                    click_status = image_info.get(image_name, -1) == self.current_id

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
            self.image_info = [{} for _ in range(5)]

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
        except FileNotFoundError:
            # Initialize folder paths with empty strings, current_id with 0, and current_image_indices with 0 for all columns
            self.folder_paths = [""] * 5
            self.current_id = 0
            self.current_image_indices = [0] * 5


    def save_settings(self):
        # Save folder paths, current_id, and current_image_indices to settings.json
        settings_data = {
            "folder_paths": [entry.get() for entry in self.folder_paths],
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
