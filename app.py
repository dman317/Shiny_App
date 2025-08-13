# offer option to use haxby data, not own data
# load mask and visualize

from shiny import App, ui, render, reactive, req
import pandas as pd
from nilearn.image import load_img
from nilearn.plotting import plot_anat
import tempfile

# UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Navigation"),
        ui.input_radio_buttons(
            "page", "", 
            {"dataset": "Dataset", "descriptive": "Descriptive", "decoding": "Decoding",
            "connectome": "Connectome"}, 
            selected="dataset")),

    ui.input_dark_mode(),  # Optional dark mode switch
    ui.output_ui("main_ui"))

# Server
def server(input, output, session):

    # Reactive expression to get uploaded file path
    @reactive.Calc
    def uploaded_anat_file():
        file = input.data_file_anat()
        if file is None or len(file) == 0:
            return None
        return file[0]["datapath"]  # Path to the uploaded file
    
    coords = reactive.Value((0,0,0))

    @reactive.effect
    @reactive.event(input.button_cut_coords)
    def apply_cut_coords():
        x = input.cut_coords_x()
        y = input.cut_coords_y()
        z = input.cut_coords_z()
        coords.set((x,y,z))
        print(f"X: {coords()[0]}, Y: {coords()[1]}, Z: {coords()[2]}")    

    # server-output -------------------------------------------------------------------------------

    @output
    @render.text
    def show_data_affine():
        path=uploaded_anat_file()
        if path is None:
            return ""
        data_anat = load_img(path)
        return data_anat.affine
    
    @output
    @render.image
    def show_img_anat():
        path=uploaded_anat_file()
        req(path)
        x,y,z = coords()
        data_anat = load_img(path)

        tmpfile = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmpfile_path = tmpfile.name
        tmpfile.close()

        # Generate and save the plot
        display = plot_anat(data_anat, cut_coords=(x,y,z))
        display.savefig(tmpfile_path)
        display.close()

        # Return file path to Shiny
        return {"src": tmpfile_path, "width": "100%", "alt": "Anatomical brain image"}


    # UI logic for different pages
    @output
    @render.ui
    def main_ui():
        if input.page() == "dataset":
            return ui.navset_tab(
                ui.nav_panel("Load", 
                    ui.input_file("data_file_anat", "Anat 3D (a single .nii-file)"),
                    ui.input_file("data_file_func", "Func 4D (a single .rar-file that contains all the relevant .nii-files)"),
                    ui.input_file("data_file_mask", "Mask"),
                    ui.input_file("data_file_events", "Events (a single .rar-file that contains all the relevant .csv-files)")),

                ui.nav_panel("View",
                             ui.row(
                                 ui.input_numeric("cut_coords_x", "x", value=0, width="100px"),
                                 ui.input_numeric("cut_coords_y", "y", value=0, width="100px"),
                                 ui.input_numeric("cut_coords_z", "z", value=0, width="100px"),
                                 ui.input_switch("switch_draw_lines", "Show Lines", True)),
                             ui.input_action_button("button_cut_coords","Apply Coordinates"),
                             ui.output_image("show_img_anat")),

                             #TODO: Action links for key structures (Motor Cortex, Visual Cortex, Hippocampus)?

                ui.nav_panel("Meta-Data",
                             ui.output_text("show_data_affine")),
                ui.nav_panel("Info",
                             ui.p("info about the requiret data structure and naming conventions for uploading")))
        
        
        elif input.page() == "descriptive":
            return ui.navset_tab(
                ui.nav_panel("Tab_Descriptive_X", ui.p("Content for Page 2 - Tab X")),
                ui.nav_panel("Tab_Descriptive_Y", ui.p("Content for Page 2 - Tab Y")),
                ui.nav_panel("Tab_Descriptive_Z", ui.p("Content for Page 2 - Tab Z"))
            )
        elif input.page() == "decoding":
            return ui.navset_tab(
                ui.nav_panel("FREM",
                             ui.p("Show if all requerements are met (all files uploaded etc.)"),
                             ui.a("Link to Nilearn - FREM", href="https://nilearn.github.io/stable/decoding/frem.html", target="_blank"),),
                ui.nav_panel("SpaceNet", ui.p("Content for Page 3 - Tab y")),
                ui.nav_panel("Searchlight", ui.p("Blaa")),
                ui.nav_panel("SVM"),
                ui.nav_panel("MLP"),
                ui.nav_panel("GCN")

            )
        elif input.page() == "connectome":
            return None

# Create and run the app
app = App(app_ui, server)


