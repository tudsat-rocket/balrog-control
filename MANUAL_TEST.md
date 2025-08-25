# UI Button Test Plan (Manual Test Bench)

## Button Inventory Checklist

### Session/Connection
- **Connect**
  - **UI Outcome**: Connection status indicator updates; error toast on failure.
  - **Physical Outcome**: Controller handshake observed; comms LEDs/heartbeat on.

### Green State
- **Go to Green State**
  - **UI Outcome**: State changes to Green; relevant controls enabled.
  - **Physical Outcome**: Valves closed; sensors calibrated; safe state achieved.
- **Calibrate Thrust Load**
  - **UI Outcome**: Calibration wizard completes; thrust load indicator updates.
  - **Physical Outcome**: -
- **Toggle (Enable/Disable) Sensor**
  - **UI Outcome**: Sensor status toggles; telemetry updates.
  - **Physical Outcome**: -
- **Dump Sensors to File**
  - **UI Outcome**: File saved confirmation; logging badge clears.
  - **Physical Outcome**: -
- **Reset Sensors**
  - **UI Outcome**: Sensor indicators reset; telemetry cleared.
  - **Physical Outcome**: -
- **Test Counter**
  - **UI Outcome**: Counter test completes; numeric display updates.
  - **Physical Outcome**: Segment display cycles through test pattern.
- **Self Check**
  - **UI Outcome**: Self-check status updates; confirmation shown.
  - **Physical Outcome**: -
- **Test Light**
  - **UI Outcome**: Light test completes; indicators update.
  - **Physical Outcome**: Lights cycle through test pattern.
- **Test Horn**
  - **UI Outcome**: Horn activation indicator flashes.
  - **Physical Outcome**: Horn sounds for 5 seconds.
- **Open File**
  - **UI Outcome**: File dialog opens; selected file loads.
  - **Physical Outcome**: -
- **Reload File**
  - **UI Outcome**: File reloads; confirmation shown.
  - **Physical Outcome**: -
- **Start Sequence**
  - **UI Outcome**: No Response.
  - **Physical Outcome**: -

### Yellow State
- **Go to Yellow State**
  - **UI Outcome**: State changes to Yellow; relevant controls enabled. If valves are not closed, it asks if the user wants to go to yellow state.
  - **Physical Outcome**: Light changes to Yellow
- **Self Check**
  - **UI Outcome**: Self-check status updates; confirmation shown.
  - **Physical Outcome**: -
- **Test Light**
  - **UI Outcome**: Light test completes; indicators update.
  - **Physical Outcome**: -
- **Test Horn**
  - **UI Outcome**: Horn activation indicator flashes.
  - **Physical Outcome**: -
- **Open File**
  - **UI Outcome**: File dialog opens; selected file loads.
  - **Physical Outcome**: -
- **Reload File**
  - **UI Outcome**: File reloads; confirmation shown.
  - **Physical Outcome**: -
- **Start Sequence**
  - **UI Outcome**: No Response
  - **Physical Outcome**: -

### Armed State
- **Go to Armed State**
  - **UI Outcome**: State changes to Armed.
  - **Physical Outcome**: Light switches to Red. Horn sounds for 5 seconds.
- **Close All Valves**
  - **UI Outcome**: Valve status indicators update to closed.
  - **Physical Outcome**: All valves close; flow stops; safe state achieved.
- **Trigger Horn**
  - **UI Outcome**: Horn activation indicator flashes.
  - **Physical Outcome**: Horn sounds for 5 seconds.
- **Arming**
  - **UI Outcome**: Arming state toggles; dangerous controls enabled.
  - **Physical Outcome**: Interlocks bypassed; valves prepared for operation.
- **Toggle N2O Main Valve**
  - **UI Outcome**: Valve status toggles; telemetry updates.
  - **Physical Outcome**: Main valve opens/closes; flow starts/stops.
- **Toggle Quick Disconnect**
  - **UI Outcome**: Disconnect status toggles; telemetry updates.
  - **Physical Outcome**: Quick disconnect engages/disengages.
- **Toggle N2 Pressure Valve**
  - **UI Outcome**: Valve status toggles; telemetry updates.
  - **Physical Outcome**: Pressure valve opens/closes; flow starts/stops.
- **Toggle N2 Purge Valve**
  - **UI Outcome**: Valve status toggles; telemetry updates.
  - **Physical Outcome**: Purge valve opens/closes; flow clears lines.
- **Toggle N2O Fill Valve**
  - **UI Outcome**: Valve status toggles; telemetry updates.
  - **Physical Outcome**: Fill valve opens/closes; flow starts/stops.
- **Run N2O Purge Sequence**
  - **UI Outcome**: Sequence starts; progress indicator updates.
  - **Physical Outcome**: Purge sequence executes; valves and sensors respond.
- **Run Ignition Sequence**
  - **UI Outcome**: Sequence starts; progress indicator updates.
  - **Physical Outcome**: Ignition sequence executes; valves and sensors respond.
- **Abort Sequence**
  - **UI Outcome**: Sequence stops; confirmation shown.
  - **Physical Outcome**: Outputs return to safe state; valves close.
- **Force Dump**
  - **UI Outcome**: Dump confirmation shown; telemetry updates.
  - **Physical Outcome**: Sensor data exported; no process impact.