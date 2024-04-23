
import os
import matplotlib
matplotlib.use('TkAgg')  # Use a non-blocking backend
import matplotlib.pyplot as plt
import numpy as np

def frame_to_sec(frame, fps):
    return (float)(frame/fps) #seconds = frame/fps
def sec_to_frame(second, fps):
    return second*fps #frame = second*fds

def frange(start, stop, step=1.0):
    while start < stop:
        yield start
        start += step

def video_frames_to_grayscale(video_frames):

    # Convert frames to grayscale
    grayscale_frames = np.mean(video_frames, axis=-1, keepdims=True).astype(np.uint8)

    return grayscale_frames

def makedirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

def save_figure(figure_name):
    if os.path.exists(figure_name):
        os.remove(figure_name)  # Delete the existing file
    
    plt.savefig(figure_name)  # Save the figure

def plot_multiple_graphs(video_path, fig_dir, graphs):
    """
    Plot multiple graphs in the same figure.

    Parameters:
        graphs: List of tuples, each containing x and y data for a graph.
    """
    plt.figure()  # Create a new figure
    for x, y in graphs:
        plt.plot(x, y)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.grid(True)
    save_figure(os.path.join(fig_dir, os.path.basename(video_path).split('.')[0] + '.jpg'))


def plot_multiple_curves(video_path, fig_dir, x, y1, y2, y1_label='Y1', y2_label='Y2', name = "plot"):
    """
    Plot two curves with different y-axes on the same graph.

    Parameters:
        x: List or array-like object containing x-axis values.
        y1: List or array-like object containing y-axis values for the first curve.
        y2: List or array-like object containing y-axis values for the second curve.
        y1_label: Label for the y1-axis.
        y2_label: Label for the y2-axis.
    """
    fig, ax1 = plt.subplots()

    # Plot the first curve with primary y-axis
    ax1.plot(x, y1, color='blue')
    ax1.set_xlabel('X-axis')
    ax1.set_ylabel(y1_label, color='blue')
    ax1.set_ylim(0, 3)

    # Create a secondary y-axis
    ax2 = ax1.twinx()
    ax2.plot(x, y2, color='red')
    ax2.set_ylabel(y2_label, color='red')
    ax2.set_ylim(0, 3)

    save_figure(os.path.join(fig_dir, name + '.jpg'))

def plot_all_info(frames, flow_magnitude, flow_magnitude_per_bar, flow_magnitude_per_bar_no_beat, scene_list, fig_dir):
    
    X = np.arange(1, frames)
    Y1 = flow_magnitude
    Y2 = flow_magnitude_per_bar
    Y3 = flow_magnitude_per_bar_no_beat
    
    plt.figure(figsize=(20, 12))  # Adjust figure size as needed
    
    # Plot Y1 with the same Y axis as Y2 and Y3
    plt.subplot(3, 1, 1)
    plt.plot(X, Y1, '-', color='blue', label="Per Frame") 
    plt.ylim(0, 2.5)  # Set Y-axis limits
    for scene in scene_list:
        plt.axvline(x=scene[0].get_frames(), color='red', linestyle='--', linewidth=1)
    plt.ylabel('Y-axis Label')  # Add Y-axis label
    plt.title('Optical Flow Magnitude')  # Add title for the first subplot
    
    # Plot Y2
    plt.subplot(3, 1, 2)
    plt.plot(X, Y2, 'r-', label='Per Bar', lw=3)  # Plot Y2
    plt.plot(X, Y1, '-', color='blue', label="Per Frame") 
    for scene in scene_list:
        plt.axvline(x=scene[0].get_frames(), color='red', linestyle='--', linewidth=1)
    plt.ylim(0, 2.5)  # Set Y-axis limits
    plt.ylabel('Y-axis Label')  # Add Y-axis label
    plt.title('Per Bar Flow')  # Add title for the second subplot
    
    # Plot Y3
    plt.subplot(3, 1, 3)
    plt.plot(X, Y3, 'r-', label='Per Bar', lw=3)  # Plot Y3
    plt.plot(X, Y1, '-', color='blue', label="Per Frame") 
    for scene in scene_list:
        plt.axvline(x=scene[0].get_frames(), color='red', linestyle='--', linewidth=1)
    plt.ylim(0, 2.5)  # Set Y-axis limits
    plt.xlabel('X-axis Label')  # Add X-axis label
    plt.ylabel('Y-axis Label')  # Add Y-axis label
    plt.title('Per Bar Flow')  # Add title for the third subplot
    
    save_figure(os.path.join(fig_dir, "final_plot" + '.jpg'))


