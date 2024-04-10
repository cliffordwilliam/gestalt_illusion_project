from constants import *


class Animator:
    '''
    How to use: 
        1: Give me animation data
        2: Starting animation
        3: Run my update callback

    What will happen:
        1: Timer counts until current animation frame duration
        2: If it is time to cycle to next frame, timer is 0 and go to next frame
        3: Check if next frame is last
        4: If it is last loop or not loop?
        5: Update owner region with updated frame
        6: If it is last and don't loop, got next animation?
        7: Got next animation? play it, reset timer and frame index
    '''

    def __init__(self, owner, animation_data, initial_animation_name):
        # Owner
        self.owner = owner

        # Animation data
        self.animation_data = animation_data

        # region current animation data
        self.current_animation = initial_animation_name
        self.is_loop = self.animation_data[self.current_animation]["is_loop"]
        self.next_animation = self.animation_data[self.current_animation]["next_animation"]
        self.frames_list = self.animation_data[self.current_animation]["frames_list"]
        self.frames_list_len = len(self.frames_list)
        self.frames_list_i_len = self.frames_list_len - 1
        self.frame_index = 0
        self.timer = 0
        # endregion current animation data

        # region frame data
        self.frame_data = self.frames_list[self.frame_index]
        self.owner.region = self.frame_data["region"]
        self.duration = self.frame_data["duration"]
        # endregion frame data

        # Callbacks
        self.listener_end = []

    def add_event_listener(self, value, event):
        if event == "animation_end":
            self.listener_end.append(value)

    def set_current_animation(self, value):
        # Calling the same animation name when it is playing will reset it to start

        # region current animation data
        self.current_animation = value
        self.is_loop = self.animation_data[self.current_animation]["is_loop"]
        self.next_animation = self.animation_data[self.current_animation]["next_animation"]
        self.frames_list = self.animation_data[self.current_animation]["frames_list"]
        self.frames_list_len = len(self.frames_list)
        self.frames_list_i_len = self.frames_list_len - 1
        self.set_frame_index(0)
        self.timer = 0
        # endregion current animation data

    def set_frame_index(self, value):
        # Update frame index
        self.frame_index = value

        # On last frame?
        if self.frame_index > self.frames_list_i_len:
            # This anim loop?
            if self.is_loop == 1:
                # Reset frame index
                self.frame_index = 0

            # This anim don't loop?
            else:
                # Stay on last frame
                self.frame_index -= 1

                # Didn't loop, this anim has transition animation?
                if self.next_animation != 0:
                    # Play next anim, do not call animation end callback
                    self.set_current_animation(self.next_animation)
                    return

                # Call animation end callback
                for callback in self.listener_end:
                    callback()

                # If staying on last frame no need to update data
                return

        # region frame data
        self.frame_data = self.frames_list[self.frame_index]
        self.owner.region = self.frame_data["region"]
        self.duration = self.frame_data["duration"]
        # endregion frame data

    def update(self, dt):
        # region update timer, set frame index
        self.timer += dt
        if self.timer >= self.duration:
            self.timer = 0
            self.set_frame_index(self.frame_index + 1)
        # endregion update timer, set frame index
