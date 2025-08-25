import time
import csv
import yaml
from pathlib import Path

from control.actor import Actor
from control.brick_handling import StackHandler
from control.definitions import ActorType


def _load_actors_from_yaml(config_path: str = 'config/balrog.yaml') -> dict[str, Actor]:
    """Parse balrog.yaml and construct Actor objects like controller._construct_actors does."""
    with open(config_path, 'r') as f:
        balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
        actors_cfg = balrog_config['actors']

    actors: dict[str, Actor] = {}
    for a in actors_cfg:
        actors[a['name']] = Actor(
            a['name'], a['type'], a['uid'], a['output'], a.get('min_position', -1), a.get('max_position', -1)
        )
    return actors


def _configure_servos(stack: StackHandler, actors: dict[str, Actor]) -> None:
    """Replicate controller._set_configuration for SERVO actors to ensure positions can be set."""
    # wait for devices to enumerate
    time.sleep(0.5)
    for actor in actors.values():
        # In config, type is stored as string (e.g., 'SERVO'). Accept either enum or string.
        if (isinstance(actor.type, ActorType) and actor.type == ActorType.SERVO) or (
            isinstance(actor.type, str) and actor.type.upper() == 'SERVO'
        ):
            brick = stack.get_device(actor.get_br_uid())
            # with 0 velocity the position is set instantly
            velocity = 0
            acceleration = 0
            deceleration = 0
            pwm_min = 500
            pwm_max = 2500
            # Configure channel on Servo V2 bricklet
            brick.set_pulse_width(actor.output, pwm_min, pwm_max)
            brick.set_motion_configuration(actor.output, velocity, acceleration, deceleration)


def _position_range(min_pos: int, max_pos: int, step: int) -> list[int]:
    """Generate an inclusive range from min_pos to max_pos using the correct step direction."""
    if step <= 0:
        raise ValueError("step must be > 0")
    if min_pos == max_pos:
        return [min_pos]
    if max_pos > min_pos:
        return list(range(min_pos, max_pos + 1, step))
    # descending
    return list(range(min_pos, max_pos - 1, -step))


def test_servo_positions(
    output_csv_path: str | Path = "servo_current_test_results.csv",
    host: str = "localhost",
    port: int = 4223,
    step: int = 100,
    delay: float = 0.5,
) -> None:
    """
    Sweep positions from configured min to max for all SERVO actors and log current draw per position.

    - Connects to TinkerForge stack via StackHandler
    - Configures Servo V2 bricklet channels
    - For each servo channel, moves through positions and records get_current()
    - Writes CSV with: timestamp, actor_name, uid, channel, position, current_mA
    """
    actors = _load_actors_from_yaml()

    # Connect to bricks
    stack = StackHandler()
    stack.start_connection(host, port)

    try:
        _configure_servos(stack, actors)

        # Open CSV file for writing
        output_csv_path = Path(output_csv_path)
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with output_csv_path.open(mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # header
            csv_writer.writerow(["timestamp", "actor", "uid", "channel", "position", "current_mA"])

            for name, actor in actors.items():
                # Only test SERVO actors
                if (isinstance(actor.type, ActorType) and actor.type == ActorType.SERVO) or (
                    isinstance(actor.type, str) and actor.type.upper() == 'SERVO'
                ):
                    brick = stack.get_device(actor.get_br_uid())
                    channel = actor.get_output()

                    positions = _position_range(actor.min_position, actor.max_position, step)

                    # Enable channel for test
                    brick.set_enable(channel, True)
                    try:
                        for pos in positions:
                            brick.set_position(channel, pos)
                            # Wait for the servo to settle
                            time.sleep(delay)
                            # Read current draw for this channel in mA
                            current = brick.get_current(channel)
                            csv_writer.writerow([
                                time.strftime('%Y-%m-%d %H:%M:%S'), name, actor.get_br_uid(), channel, pos, current
                            ])
                    finally:
                        # Disable channel after testing
                        brick.set_enable(channel, False)
    finally:
        # Always disconnect
        stack.stop_connection()


if __name__ == "__main__":
    # Defaults chosen for local brickd
    test_servo_positions(
        output_csv_path="servo_current_test_results.csv",
        host="localhost",
        port=4223,
        step=100,
        delay=0.6,
    )
