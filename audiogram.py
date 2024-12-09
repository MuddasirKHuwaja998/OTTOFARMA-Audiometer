import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .config import *


# Maybe add option of date as subtitle. Subtitle is already implemented, but not used.

freq_levels = {125: 20, 250: 20, 500: 20, 1000: 20, 2000: 20, 4000: 20, 8000: 20}

def split_values(x_vals:list, values:list, target_values:np.array)->tuple:
    """Helper function. Splits values into "heard" and "not heard" arrays.

    Args:
        x_vals (list of int): indices of values
        values (list of float and str): list of hearing levels and 'NH' if a sound was not heard
        target_values (np.array): target value for "not heard" array

    Returns:
        np.array: indices of heard array
        np.array: values of heard array
        np.array: indices of "not heard" array
        np.array: values of "not heard" array
    """
    heard = np.array([[i, int(v)] for i, v in zip(x_vals, values) if v != 'NH' and v != None]).T
    if len(heard) == 0:
        heard_i, heard_level = [], []
    else:
        heard_i, heard_level = heard

    not_heard = np.array([[i, t] for i, v, t in zip(x_vals, values, target_values) if v == 'NH' and v != None]).T
    if len(not_heard) == 0:
        not_heard_i, not_heard_level = [], []
    else:
        not_heard_i, not_heard_level = not_heard

    return np.array(heard_i, dtype=int), np.array(heard_level, dtype=int), np.array(not_heard_i, dtype=int), np.array(not_heard_level, dtype=int)
  
def filter_none(x_vals:list, values:list)->tuple:
    """Helper function. Removes None or NaN values from list.

    Args:
        x_vals (list of int): indices of values
        values (list of float): list of hearing levels

    Returns:
        np.array: indices of values
        np.array: array of hearing levels
    """
    filtered = np.array([[i, v] for i, v in zip(x_vals, values) if v not in (None, "NaN")]).T
    if len(filtered) == 0:
        return np.array([], dtype=int), np.array([], dtype=int)
    i_vals, v_vals = filtered
    
    return np.array(i_vals, dtype=int), np.array(v_vals, dtype=int)

def create_audiogram(freqs:list, left_values:list=None, right_values:list=None, binaural:bool=False, name:str="audiogram.png", freq_levels:dict=freq_levels, subtitle:str=None):
    """
    Creates an audiogram based on the given frequencies and hearing threshold values with custom x-axis labels.

    Args:
        freqs (list of int): A list of frequencies in Hz.
        left_values (list of int, optional): A list of hearing thresholds in dB HL for the left ear. Defaults to None.
        right_values (list of int, optional): A list of hearing thresholds in dB HL for the right ear. Defaults to None.
        binaural (bool, optional): Whether the audiogram is made from binaural test values. Defaults to False.
        name (str, optional): The name of the saved audiogram file. Defaults to "audiogram.png".
        freq_levels (dict, optional): A dictionary mapping frequencies to their target values. Defaults to freq_levels.
        subtitle (str, optional): A subtitle for the audiogram. Defaults to None.
    """

    print("Creating audiogram with frequencies:", freqs)
    print("Left ear values:", left_values)
    print("Right ear values:", right_values)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.axhspan(-10, 20, facecolor='lightgreen', alpha=0.2)
    ax.axhspan(20, 40, facecolor='lightskyblue', alpha=0.2)
    ax.axhspan(40, 70, facecolor='yellow', alpha=0.2)
    ax.axhspan(70, 90, facecolor='orange', alpha=0.2)
    ax.axhspan(90, 120, facecolor='red', alpha=0.2)

    t1 = ax.text(6.4, 5, 'Normal belonging\nGreen: (Normal belonging):', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t2 = ax.text(6.4, 30, 'Lightweight - Heavy duty\n Blue: (Mild hearing loss)', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t3 = ax.text(6.4, 55, 'Mittlere - Heavy duty\n Yellow: (Moderate hearing loss)', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t4 = ax.text(6.4, 80, 'Heavy - Heavy duty\n Orange : (Severe hearing loss)', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t5 = ax.text(6.4, 105, 'High-grade dependability Red : (Profound hearing loss)', ha='left', va='center', fontsize=TEXT_FONT_SIZE)

    x_vals = range(len(freqs))
    target_values = np.array(list(freq_levels.values()))

    nan_freqs_left = [freq for i, freq in zip(left_values, freqs) if i == 'NaN']
    nan_freqs_right = [freq for i, freq in zip(right_values, freqs) if i == 'NaN']

    nan_text = ""
    nan_t = False

    if 'NH' in left_values or 'NH' in right_values:
        heard_i_left, heard_level_left, not_heard_i_left, not_heard_level_left = split_values(x_vals, left_values, target_values)
        heard_i_right, heard_level_right, not_heard_i_right, not_heard_level_right = split_values(x_vals, right_values, target_values)

        if binaural:
            ax.plot(x_vals, target_values, linestyle='-', color=COLOR_BINAURAL)
            ax.plot(heard_i_left, heard_level_left, marker=MARKER_BINAURAL, markersize=MARKER_SIZE, linestyle='None', color=COLOR_BINAURAL, label='Sentito')
            ax.plot(not_heard_i_left, not_heard_level_left, marker=NOT_HEARD_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', color=COLOR_BINAURAL, label='No Sentito')
        else:
            ax.plot(x_vals, target_values, linestyle='-', color=COLOR_RIGHT)
            ax.plot(heard_i_right, heard_level_right, marker=MARKER_RIGHT, markersize=MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markerfacecolor='none', markeredgewidth=MARKER_EDGE_WIDTH, label='Sentito dall orecchio destro')
            ax.plot(not_heard_i_right, not_heard_level_right, marker=NOT_HEARD_RIGHT_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markeredgewidth=MARKER_EDGE_WIDTH, label='Non sentito dall orecchio destro')
            ax.plot(x_vals, target_values+SHIFT, linestyle='-', color=COLOR_LEFT)
            ax.plot(heard_i_left, heard_level_left+SHIFT, marker=MARKER_LEFT, markersize=MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='Orecchio sinistro')
            ax.plot(not_heard_i_left, not_heard_level_left+SHIFT, marker=NOT_HEARD_LEFT_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='lasciato non sentito')

    else:
        x_vals_left, left_values = filter_none(x_vals, left_values)
        x_vals_right, right_values = filter_none(x_vals, right_values)

        if binaural:
            ax.plot(x_vals_left, left_values, marker=MARKER_BINAURAL, markersize=MARKER_SIZE, linestyle='-', color=COLOR_BINAURAL, label='binaural')
        else:
            ax.plot(x_vals_right, right_values, marker=MARKER_RIGHT, markersize=MARKER_SIZE, linestyle='-', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markeredgewidth=MARKER_EDGE_WIDTH, markerfacecolor='none', label='Orecchio destro')
            ax.plot(x_vals_left, left_values+SHIFT, marker=MARKER_LEFT, markersize=MARKER_SIZE, linestyle='-', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='Orecchio sinistro')

        if nan_freqs_left or nan_freqs_right:
            and_str = ""
            nan_text = "No value could be determined for the following frequencies:\n"
            print(nan_freqs_left, nan_freqs_right)
            if nan_freqs_left:
                nan_text += f"links: {', '.join(map(str, nan_freqs_left))} "
                and_str = "und "
            if nan_freqs_right:
                nan_text += f"{and_str}rechts: {', '.join(map(str, nan_freqs_right))}"
            nan_t = ax.text(0.05, -0.2, nan_text, transform=ax.transAxes, fontsize=TEXT_FONT_SIZE, ha='left', va='top', bbox=dict(facecolor='None', edgecolor='None'))

    ax.invert_yaxis()
    
    if subtitle:
        title = fig.suptitle('Audiogram', fontsize=HEADER_SIZE, y=1.02) 
        ax.set_title(subtitle, fontsize=LABEL_FONT_SIZE, pad=20)
    else:
        title = fig.suptitle('Audiogram', fontsize=HEADER_SIZE) 
    
    ax.set_xlabel('Frequency (Hz)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Decibel (dB HL)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylim(120, -10)
    ax.set_xticks(range(len(freqs)))
    ax.set_xticklabels([f"{int(freq)}" for freq in freqs], fontsize=TICK_FONT_SIZE)
    ax.set_yticks(np.arange(0, 121, 10))
    ax.set_yticklabels(np.arange(0, 121, 10), fontsize=TICK_FONT_SIZE)
    ax.grid(True, which='Entrambi', linestyle='--', linewidth=0.5)
    lgd = ax.legend(loc='in alto a sinistra', bbox_to_anchor=(1.15, 0.205), fontsize=LEGEND_FONT_SIZE, frameon=False, labelspacing=1)
    
    if nan_t:
        fig.savefig(name, bbox_extra_artists=(title, lgd, t1, t2, t3, t4, t5, nan_t), bbox_inches='tight')
    else:
        fig.savefig(name, bbox_extra_artists=(title, lgd, t1, t2, t3, t4, t5), bbox_inches='tight')
    
    plt.close(fig)

