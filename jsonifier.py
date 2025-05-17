"""
File: jsonifier.py

Converts a parsed buffer to JSON-friendly format.
"""

import os
from parser import Parser
from sfztypes import Header, OpCodeHeader

def make_sample_dictionary(parsed: Parser):
    """
    Takes the parsed data and makes sample lists.
    Returns a dictionary of group names and associated sample lists. The layout is
    {
        "group1: [
            [
                {"sample": "path to sample", ...}, ...
            ], ...
        ], ...
    }
    There are 128 lists inside each group, corresponding to the 128 MIDI notes.
    If a sample group doesn't support some MIDI notes, the corresponding lists will be empty.
    """
    sample_dict = {}

    # We start by making a default group in case the file doesn't have any groups
    current_group = Header(OpCodeHeader.GROUP)
    current_group.attributes["group_label"] = "default"
    
    # Track if the group is used (hopefully the default group we make isn't used)
    # Groups that aren't used won't be added to the sample list
    group_used = False

    # The current collection of notes
    current_collection = [[] for _ in range(128)]  # one entry for each possible note
    
    # The default path (if it needs to be updated for the samples)
    default_path = ""

    for i in range(len(parsed.parsed_buf)):
        if type(parsed.parsed_buf[i]) == Header:
            # if we've found a control group, we might need to update the default path
            if parsed.parsed_buf[i].header == OpCodeHeader.CONTROL:
                if "default_path" in parsed.parsed_buf[i].attributes:
                    default_path = parsed.parsed_buf[i].attributes["default_path"]
            
            # if we've found a new group and need to add the existing group
            if parsed.parsed_buf[i].header == OpCodeHeader.GROUP:
                if group_used:
                    group_label = "group"
                    if "group_label" in current_group.attributes:
                        group_label = current_group.attributes["group_label"]
                    sample_dict[group_label] = current_collection
                group_used = False
                current_group = parsed.parsed_buf[i]
                current_collection = [[] for _ in range(128)]

            # if we've found a sample
            elif parsed.parsed_buf[i].header == OpCodeHeader.REGION:
                # do we have a low key and high key range?
                if "lokey" in parsed.parsed_buf[i].attributes and "hikey" in parsed.parsed_buf[i].attributes and "pitch_keycenter" in parsed.parsed_buf[i].attributes:
                    for midi_pitch in range(parsed.parsed_buf[i].attributes["lokey"], parsed.parsed_buf[i].attributes["hikey"] + 1):
                        new_sample = {}
                        for key, val in parsed.parsed_buf[i].attributes.items():
                            if key not in ["lokey", "hikey", "pitch_keycenter"]:
                                new_sample[key] = val
                        if "tune" in new_sample:
                            new_sample["tune"] += (midi_pitch - parsed.parsed_buf[i].attributes["pitch_keycenter"]) * 100
                        else:
                            new_sample["tune"] = (midi_pitch - parsed.parsed_buf[i].attributes["pitch_keycenter"]) * 100

                        # Update the sample path
                        if "sample" in new_sample:
                            new_sample["sample"] = os.path.join(default_path, new_sample["sample"])

                        current_collection[midi_pitch].append(new_sample)
                        group_used = True
                # or do we just have a pitch center? If no pitch center, at this point we won't add the note
                elif "pitch_keycenter" in parsed.parsed_buf[i].attributes:
                    new_sample = parsed.parsed_buf[i].attributes.copy()
                    # Update the sample path
                    if "sample" in new_sample:
                        new_sample["sample"] = os.path.join(default_path, new_sample["sample"])
                    current_collection[parsed.parsed_buf[i].attributes["pitch_keycenter"]].append(new_sample)
                    group_used = True
    
    # add in the last group
    if group_used:
        group_label = "group"
        if "group_label" in current_group.attributes:
            group_label = current_group.attributes["group_label"]
        sample_dict[group_label] = current_collection

    return sample_dict