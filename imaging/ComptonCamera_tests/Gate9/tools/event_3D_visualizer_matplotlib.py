import sys
import pandas as pd
import uproot
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSplitter
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.event_ids = df['eventID'].unique()
        self.current_event_index = 0
        self.table_visible = True
        self.removed_points = []  # Store removed points information

        self.initUI()

    def initUI(self):
        self.resize(1600, 600)
        self.setWindowTitle("3D Event Viewer with Optional Event Data Table")

        # Main layout and splitter
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.splitter = QSplitter(self)
        layout.addWidget(self.splitter)

        # Left side: Matplotlib figure and canvas for 3D plot
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_widget.setMinimumWidth(600)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        self.splitter.addWidget(plot_widget)

        # Right side: Table for event data
        self.table_display = QTableWidget()
        self.table_display.setMinimumWidth(1000)
        self.splitter.addWidget(self.table_display)

        # Control buttons for navigation and table toggle
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Event")
        self.next_button = QPushButton("Next Event")
        self.toggle_table_button = QPushButton("Toggle Table")
        self.print_button = QPushButton("Print Event Data")
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.toggle_table_button)
        button_layout.addWidget(self.print_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.next_button.clicked.connect(self.next_event)
        self.prev_button.clicked.connect(self.prev_event)
        self.toggle_table_button.clicked.connect(self.toggle_table)
        self.print_button.clicked.connect(self.print_event_data)

        # Connect mouse click on canvas
        self.canvas.mpl_connect('pick_event', self.on_pick)

        # Initial view updates
        self.plot_event()
        self.update_event_table()

    def plot_event(self):
        """Plots the 3D points for the current eventID with PDGEncoding color mapping."""
        self.figure.clear()

        # Get current event data
        current_event_id = self.event_ids[self.current_event_index]
        event_data = self.df[self.df['eventID'] == current_event_id]

        # Remove points that were deleted in the current event
        if self.removed_points:
            event_data = event_data[
                ~event_data.apply(lambda row: (
                                                  row['localPosX'],
                                                  row['localPosY'],
                                                  row['localPosZ']
                                              ) in self.removed_points, axis=1)
            ]

        # Extract positions and other data
        x = event_data['localPosX']
        y = event_data['localPosY']
        z = event_data['localPosZ']
        track_ids = event_data['trackID']
        pdg_encoding = event_data['PDGEncoding']

        # Define color mapping for PDGEncoding
        color_map = {11: 'red', 22: 'green'}  # 11 (e-) -> red, 22 (gamma) -> green

        # Start 3D plotting
        ax = self.figure.add_subplot(111, projection='3d')

        # Scatter plot for e- (PDGEncoding == 11)
        e_minus_data = event_data[event_data['PDGEncoding'] == 11]
        ax.scatter(e_minus_data['localPosX'], e_minus_data['localPosY'], e_minus_data['localPosZ'],
                                     c=color_map[11], label="e-", marker='o', picker=True)

        # Scatter plot for gamma (PDGEncoding == 22)
        gamma_data = event_data[event_data['PDGEncoding'] == 22]
        ax.scatter(gamma_data['localPosX'], gamma_data['localPosY'], gamma_data['localPosZ'],
                                   c=color_map[22], label="gamma", marker='^')

        # Add annotations
        for i in range(len(event_data)):
            ax.text(x.iloc[i], y.iloc[i], z.iloc[i], f"{track_ids.iloc[i]}", fontsize=8, color='blue')

        # Labels, title, and legend
        ax.set_title(f"Event ID: {current_event_id}")
        ax.set_xlabel("localPosX")
        ax.set_ylabel("localPosY")
        ax.set_zlabel("localPosZ")
        ax.legend(loc="upper right")

        # Redraw canvas
        self.canvas.draw()

    def on_pick(self, event):
        """Handles mouse click events for point removal."""
        if hasattr(event, 'artist'):  # Check if the clicked object is a point
            artist = event.artist
            if isinstance(artist, plt.Line2D):  # Verify it's a scatter point
                xdata, ydata, zdata = artist.get_offsets().data.T

                # Find the picked point coordinates
                ind = event.ind[0]  # Get the index of the picked point
                picked_x = xdata[ind]
                picked_y = ydata[ind]
                picked_z = zdata[ind]

                # Save to removed points and re-plot
                self.removed_points.append((picked_x, picked_y, picked_z))
                self.plot_event()

    def update_event_table(self):
        """Displays rows corresponding to the current event in a table widget."""
        self.table_display.clear()

        # Get current event's data
        current_event_id = self.event_ids[self.current_event_index]
        event_data = self.df[self.df['eventID'] == current_event_id]

        # Drop unnecessary columns
        columns_to_drop = [
            'runID', 'time', 'stepLength', 'trackLength', 'posX', 'posY', 'posZ',
            'localPosX', 'localPosY', 'localPosZ', 'nCrystalCompt', 'nCrystalRayl',
            'nCrystalConv', 'layerName', 'volumeID', 'trackLocalTime', 'sourcePosX',
            'sourcePosY', 'sourcePosZ', 'sourceE_funcnergy', 'sourcePDG'
        ]
        cleaned_event_data = event_data.drop(columns=columns_to_drop, errors='ignore')

        # Update table structure
        self.table_display.setColumnCount(len(cleaned_event_data.columns))
        self.table_display.setRowCount(len(cleaned_event_data.index))
        self.table_display.setHorizontalHeaderLabels(cleaned_event_data.columns)

        # Populate table
        for i, (index, row) in enumerate(cleaned_event_data.iterrows()):
            for j, value in enumerate(row):
                value = round(value, 3) if isinstance(value, float) else value
                self.table_display.setItem(i, j, QTableWidgetItem(str(value)))

    def next_event(self):
        """Go to the next event."""
        if self.current_event_index < len(self.event_ids) - 1:
            self.current_event_index += 1
            self.plot_event()
            self.update_event_table()

    def prev_event(self):
        """Go to the previous event."""
        if self.current_event_index > 0:
            self.current_event_index -= 1
            self.plot_event()
            self.update_event_table()

    def toggle_table(self):
        """Show or hide the event data table."""
        if self.table_visible:
            self.splitter.widget(1).hide()
        else:
            self.splitter.widget(1).show()
        self.table_visible = not self.table_visible

    def print_event_data(self):
        """Print the DataFrame rows corresponding to the currently displayed event."""
        current_event_id = self.event_ids[self.current_event_index]
        event_data = self.df[self.df['eventID'] == current_event_id]
        print(event_data)


# Load ROOT file and initialize GUI
def main():
    # Read the ROOT file into a DataFrame
    file_path = "../output/"
    tree = uproot.open(file_path + "CC_Hits.root:Hits")
    df = tree.arrays(library="pd")

    # Unit conversions
    df['edep'] *= 1000  # To keV
    df['energyIniT'] *= 1000  # To keV
    df['energyFinal'] *= 1000  # To keV
    df['localPosX'] *= 1000  # To micrometers (um)
    df['localPosY'] *= 1000  # To micrometers (um)
    df['localPosZ'] *= 1000  # To micrometers (um)

    # Launch PyQt5 app
    app = QApplication(sys.argv)
    main_window = MainWindow(df)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
