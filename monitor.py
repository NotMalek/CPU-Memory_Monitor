import psutil
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Use the 'TkAgg' backend for interactive plots
matplotlib.use('TkAgg')

# Initialize the plot
fig, ax = plt.subplots()
ax.set_ylim(0, 100)
ax.set_xlim(0, 100)
ax.set_title('CPU and Memory Utilization')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Usage (%)')

# Create lines for CPU and memory usage
cpu_line, = ax.plot([], [], label='CPU', color='orange')
mem_line, = ax.plot([], [], label='Memory', color='red')
ax.legend()

# Text elements for displaying CPU and memory usage percentages
cpu_text = ax.text(0.8, 0.7, '', transform=ax.transAxes)
mem_text = ax.text(0.8, 0.6, '', transform=ax.transAxes)

# Function to update the plot
def update(frame):
    # Get the current CPU and memory usage
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent

    # Update the data for the lines
    cpu_line.set_data(list(range(frame)), [cpu_usage] * frame)
    mem_line.set_data(list(range(frame)), [mem_usage] * frame)

    # Update the text with the latest usage values
    cpu_text.set_text(f'CPU: {cpu_usage:.1f}%')
    mem_text.set_text(f'Memory: {mem_usage:.1f}%')

    return cpu_line, mem_line, cpu_text, mem_text

# Set up the animation
ani = FuncAnimation(fig, update, frames=100, interval=1000, blit=True)

# Style the lines
for line in [cpu_line, mem_line]:
    line.set_linewidth(2)
    line.set_marker('o')
    line.set_markersize(5)

# Set the background color of the plot area
ax.set_facecolor('#EFEFEF')

# Display the plot
plt.show()
