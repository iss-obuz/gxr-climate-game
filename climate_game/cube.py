from collections import deque
import random
import time


class CubeManager:
    """A class that manages the behaviors of cubes."""

    def __init__(self, client):
        self.client = client
        self.size = 5  # The size of the grid
        self.removed_cubes = deque([])
        self.avaliable_cubes = []
        self.cubeScale = {}

    def _get_anchor_name(self, x, y, z):
        return f"commons_resource_anchor{x}{y}{z}"

    def _get_object_name(self, x, y, z):
        return f"commons_resource{x}{y}{z}"

    def disable_object(self, x, y, z):
        self.client.PushCommand("disable_object", self._get_object_name(x, y, z))

    def spawn_all_objects(self):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.spawn_object(x, y, z)

    def scale_all_objects(self):
        d = self.cubeScale.copy()
        for k, v in d.items():
            if k not in self.removed_cubes and v < 0.1:
                self.client.PushCommand("set_object_scale", f"{k} {v},{v},{v} 0.1")

    def set_color_all_objects(self, color):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.set_object_color(x, y, z, color, "0.1")

    def spawn_object(self, x, y, z):
        anchor_name = self._get_anchor_name(x, y, z)
        object_name = self._get_object_name(x, y, z)
        self.client.PushCommand(
            "spawn_object", f"commons_resource {object_name} {anchor_name}"
        )
        self.client.PushCommand("enable_object", object_name)
        self.client.PushCommand("set_object_color", f"{object_name} #777777 0.0")
        self.avaliable_cubes.append(object_name)

    def set_object_color(self, x, y, z, color, transition_time=2.0):
        object_name = self._get_object_name(x, y, z)
        self.client.PushCommand(
            "set_object_color", f"{object_name} {color} {transition_time}"
        )

    def create_wave_pattern(self, color, wave_interval=0.1, transition_time=2.0):
        for i in range(1, self.size * 2):  # Creating a wave that moves through the grid
            for x in range(1, self.size + 1):
                for y in range(1, self.size + 1):
                    for z in range(1, self.size + 1):
                        if x + y + z == i:
                            self.set_object_color(x, y, z, color, transition_time)
            time.sleep(wave_interval)

    def random_flash_pattern(self, flash_count=10, transition_time=0.5):
        for _ in range(flash_count):
            x = random.randint(1, self.size)
            y = random.randint(1, self.size)
            z = random.randint(1, self.size)
            # Generates a shade of blue, transitioning to white
            shade = random.randint(0, 255)
            color = f"#{shade:02X}{shade:02X}FF"
            self.set_object_color(x, y, z, color, transition_time)

    def disable_all_objects(self):
        for x in range(1, self.size + 1):
            for y in range(1, self.size + 1):
                for z in range(1, self.size + 1):
                    self.disable_object(x, y, z)

    def sync_with_Et(self, Et, EK):
        d = self.cubeScale.copy()
        # to remove from smalest to higest
        for k, v in sorted(d.items(), key=lambda x: x[1]):
            if (
                Et < EK - len(self.removed_cubes)
                and v < 0.1
                and k not in self.removed_cubes
            ):  #
                self.client.PushCommand("disable_object", k)
                self.removed_cubes.append(k)
                self.avaliable_cubes.remove(k)
            else:
                # When regenerating the environment, it can also be so that more than one cube is renewed at once
                while Et > EK - len(self.removed_cubes) and len(self.removed_cubes) > 0:
                    q = self.removed_cubes.popleft()
                    self.avaliable_cubes.append(q)
                    scl = 0.1
                    self.cubeScale[q] = scl
                    self.client.PushCommand("enable_object", q)
                    self.client.PushCommand(
                        "set_object_scale", f"{q} {scl},{scl},{scl} 0.1"
                    )
        # Note that any shot can exhaust more than one cube, so if you run out of hits, then randomly take the missed ones as well
        while Et < EK - len(self.removed_cubes):
            rand_k = random.choice(self.avaliable_cubes)
            self.client.PushCommand("disable_object", rand_k)
            self.removed_cubes.append(rand_k)
            self.avaliable_cubes.remove(rand_k)
