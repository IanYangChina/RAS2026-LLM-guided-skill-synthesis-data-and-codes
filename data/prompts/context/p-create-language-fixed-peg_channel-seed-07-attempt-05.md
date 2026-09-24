## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2605 | 0.66 | ✅ accepted |
| 4 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1259 | 0.27 | ❌ rejected |
| 3 | approach → contact → push | arc_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3374 | 0.57 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3097 | 0.49 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1068 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.260) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align_to_entry
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_threshold:
      type: scalar
      range:
      - 10.0
      - 35.0
      default: 25.0
      binds_to:
      - path: guards.push_contact.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_entry** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.04]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_threshold: status=consumed; consumers=guards.push_contact.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.260
- **task_score** (E): 0.658
- **fitness_score**: 0.520  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_entry | 1.00 | 1.00 | 0.2730 |
| approach_peg | 1.00 | 1.00 | 0.0056 |
| contact_peg | 1.00 | 1.00 | 0.0125 |
| push_through | 0.33 | 1.00 | 0.0383 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.120, 0.040) | (0.509, 0.098, 0.040)→(0.503, 0.084, 0.035) | 0.179→0.165 | 1.00 / 1.333 | 1.079 | 20.117 |
| approach_peg | approach | 1.00 / step_budget | (0.496, 0.120, 0.040)→(0.498, 0.121, 0.036) | (0.503, 0.084, 0.035)→(0.503, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.497 | 0.988 |
| contact_peg | contact | 1.00 / force_exceeded | (0.498, 0.121, 0.036)→(0.497, 0.110, 0.031) | (0.503, 0.084, 0.034)→(0.503, 0.081, 0.035) | 0.164→0.161 | 1.00 / 2.333 | 1311.209 | 6.610 |
| push_through | push | 0.33 / guard_failure | (0.497, 0.023, 0.029)→(0.498, -0.016, 0.029) | (0.503, 0.081, 0.035)→(0.503, -0.045, 0.037) | 0.161→0.039 | 1.00 / 2.000 | 7.635 | 28.020 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.908
- alignment_error: None
- force_efficiency: 0.321
- terminal_score: 0.908
- phase_score: 0.341
- phase_breakdown.approach_score: 0.475
- phase_breakdown.contact_score: 0.579
- phase_breakdown.push_score: 0.217

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.568
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.908
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.371


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39098,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.08434,"align_to_entry.speed":0.14408,"approach_peg.speed":0.11649,"contact_peg.contact_force":5.05618,"contact_peg.speed":0.02473,"push_through.push_distance":0.12002,"push_through.push_force_threshold":27.87783,"push_through.push_speed":0.048,"push_through.push_tolerance":0.03555},"optimized_scores":{"best_composite_score":0.30773,"best_fitness_score":0.56773,"best_task_score":0.90805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":61.0,"contact_point_centroid":[0.50083,0.11468,0.04689],"force_p95":30.5631,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.93784,"mean_force":8.13594,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49631,0.12591,0.04171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":913.0,"contact_point_centroid":[0.50374,0.10982,0.00941],"force_p95":0.81659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.5241,"mean_force":0.98318,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.4977,0.20359,0.15319]},{"body_a":"attachment","body_b":"peg","contact_count":132.0,"contact_point_centroid":[0.50333,0.04921,0.0416],"force_p95":10.22894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.88449,"mean_force":2.1156,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49892,0.06056,0.02757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.5062,0.01351,0.00971],"force_p95":12.67313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.75572,"mean_force":4.60717,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49932,0.05625,0.02791]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":72.0,"contact_point_centroid":[0.5254,0.0967,0.03281],"force_p95":13.47427,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.68411,"mean_force":3.04896,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49711,0.13795,0.09746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52514,0.0383,0.02628],"force_p95":4.2417,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.50361,"mean_force":1.1535,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4986,0.06713,0.0275]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50427,0.099,0.0568],"force_p95":5.16169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.39827,"mean_force":1.70163,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49817,0.11079,0.02894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.5066,0.07785,0.00941],"force_p95":1.99054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.01726,"mean_force":0.73903,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49866,0.11311,0.03007]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52508,0.08026,0.05963],"force_p95":2.24985,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33371,"mean_force":0.69582,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49817,0.11006,0.02876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.50572,0.07836,0.00959],"force_p95":0.89488,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1637,"mean_force":0.59996,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49772,0.11304,0.0347]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50256,0.09876,0.06049],"force_p95":0.9176,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.00281,"mean_force":0.39485,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49624,0.11037,0.03633]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52519,0.08239,0.01055],"force_p95":0.82474,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89604,"mean_force":0.47017,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49616,0.11023,0.03681]}],"total_contact_groups":12},"final_pose_error":0.03553,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50608,-0.03351,0.03503],"final_tcp_position":[0.50209,-0.00438,0.02897],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":33.93784,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.50765,0.0823,0.0357],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.16253,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":1.33158,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1046.0,"raw_peak_contact_force":33.93784,"tcp_end":[0.49621,0.11055,0.03762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.50653,0.08163,0.03381],"object_pos_start":[0.50765,0.0823,0.0357],"object_to_goal_dist_end":0.16188,"object_to_goal_dist_start":0.16253,"object_z_max":0.0357,"peak_contact_force":0.54838,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":98.0,"raw_peak_contact_force":1.1637,"subtask_id":"approach","tcp_end":[0.50005,0.11668,0.03265],"tcp_start":[0.49621,0.11055,0.03762],"tcp_to_object_dist_end":0.03567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":103.0,"n_steps_budget":660.0,"object_pos_end":[0.50686,0.08094,0.03497],"object_pos_start":[0.50653,0.08163,0.03381],"object_to_goal_dist_end":0.16117,"object_to_goal_dist_start":0.16188,"object_z_max":0.03494,"peak_contact_force":5.39827,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":124.0,"raw_peak_contact_force":5.39827,"subtask_id":"contact","tcp_end":[0.49817,0.10988,0.02872],"tcp_start":[0.50005,0.11668,0.03265],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.03351,0.03503],"object_pos_start":[0.50686,0.08094,0.03497],"object_to_goal_dist_end":0.04715,"object_to_goal_dist_start":0.16117,"object_z_max":0.03823,"peak_contact_force":6.1125,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":268.0,"raw_peak_contact_force":15.88449,"subtask_id":"push","tcp_end":[0.50209,-0.00438,0.02897],"tcp_start":[0.49817,0.10988,0.02872],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28736,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.10323,"align_to_entry.speed":0.12241,"approach_peg.speed":0.10511,"contact_peg.contact_force":4.45029,"contact_peg.speed":0.02302,"push_through.push_distance":0.1573,"push_through.push_force_threshold":25.3285,"push_through.push_speed":0.03264,"push_through.push_tolerance":0.03651},"optimized_scores":{"best_composite_score":0.24894,"best_fitness_score":0.50894,"best_task_score":0.68115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47465,0.00509,0.0469],"force_p95":19.41112,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.21227,"mean_force":3.47662,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49212,0.03593,0.02963]},{"body_a":"attachment","body_b":"peg","contact_count":139.0,"contact_point_centroid":[0.49572,0.06989,0.0432],"force_p95":7.45388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.80735,"mean_force":2.00197,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49175,0.08136,0.03048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":964.0,"contact_point_centroid":[0.49609,0.11902,0.00943],"force_p95":0.61341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.53004,"mean_force":0.60606,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49768,0.22005,0.15614]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.4972,0.13569,0.05282],"force_p95":15.32764,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.60337,"mean_force":3.56718,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49633,0.14756,0.04061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.49874,0.05497,0.00976],"force_p95":9.09662,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.24278,"mean_force":3.53879,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49178,0.09182,0.03081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.49546,0.10372,0.00943],"force_p95":1.75564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13001,"mean_force":0.86626,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49383,0.13955,0.03491]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49622,0.12736,0.05335],"force_p95":4.15565,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.93661,"mean_force":1.03982,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49351,0.13905,0.03448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49733,0.09064,0.00919],"force_p95":1.11115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24902,"mean_force":0.61821,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49584,0.14068,0.038]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.50022,0.20005,0.29785]}],"total_contact_groups":9},"final_pose_error":0.06065,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49609,-0.0205,0.03967],"final_tcp_position":[0.49254,0.01103,0.02959],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":29.21227,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.10807,0.03405],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.18821,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":1.35773,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":22.53004,"tcp_end":[0.49633,0.14107,0.03896],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49574,0.10668,0.03511],"object_pos_start":[0.49603,0.10807,0.03405],"object_to_goal_dist_end":0.1868,"object_to_goal_dist_start":0.18821,"object_z_max":0.03509,"peak_contact_force":0.39721,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":1.24902,"subtask_id":"approach","tcp_end":[0.49526,0.14109,0.03673],"tcp_start":[0.49633,0.14107,0.03896],"tcp_to_object_dist_end":0.03445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":45.0,"n_steps_budget":690.0,"object_pos_end":[0.49613,0.10796,0.03425],"object_pos_start":[0.49574,0.10668,0.03511],"object_to_goal_dist_end":0.18809,"object_to_goal_dist_start":0.1868,"object_z_max":0.03511,"peak_contact_force":9.13001,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":61.0,"raw_peak_contact_force":9.13001,"subtask_id":"contact","tcp_end":[0.49286,0.13738,0.03353],"tcp_start":[0.49526,0.14109,0.03673],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,-0.01871,0.03954],"object_pos_start":[0.49613,0.10796,0.03425],"object_to_goal_dist_end":0.06142,"object_to_goal_dist_start":0.18809,"object_z_max":0.03963,"peak_contact_force":0.05742,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":237.0,"raw_peak_contact_force":29.21227,"subtask_id":"push","tcp_end":[0.49254,0.01103,0.02959],"tcp_start":[0.49255,0.01152,0.02963],"tcp_to_object_dist_end":0.03156,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14737,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.arc_height":0.04818,"align_to_entry.speed":0.10299,"approach_peg.speed":0.18658,"contact_peg.contact_force":7.32616,"contact_peg.speed":0.03115,"push_through.push_distance":0.16226,"push_through.push_force_threshold":34.80744,"push_through.push_speed":0.01517,"push_through.push_tolerance":0.01289},"optimized_scores":{"best_composite_score":0.2248,"best_fitness_score":0.4848,"best_task_score":0.38624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":474.0,"contact_point_centroid":[0.50352,0.00308,0.04325],"force_p95":11.23751,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.96253,"mean_force":3.89099,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49855,0.01474,0.028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50753,-0.10033,0.06017],"force_p95":36.62076,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.88065,"mean_force":21.84563,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50094,-0.05281,0.02937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50618,-0.03164,0.00993],"force_p95":11.34313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.54055,"mean_force":5.88482,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49861,0.01431,0.02806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":402.0,"contact_point_centroid":[0.52509,-0.01529,0.02588],"force_p95":4.33423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.9993,"mean_force":1.04818,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49855,0.01344,0.02798]},{"body_a":"attachment","body_b":"peg","contact_count":167.0,"contact_point_centroid":[0.50291,0.07631,0.04349],"force_p95":3.71344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.30185,"mean_force":2.28051,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4982,0.08798,0.0307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50664,0.05418,0.0096],"force_p95":3.25554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.29024,"mean_force":1.37967,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49709,0.09424,0.03187]},{"body_a":"peg","body_b":"channel_base_body","contact_count":897.0,"contact_point_centroid":[0.50582,0.06301,0.00937],"force_p95":0.55575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56165,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.49745,0.17924,0.15562]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":97.0,"contact_point_centroid":[0.52504,0.05751,0.03324],"force_p95":2.23668,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.50704,"mean_force":1.20805,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4986,0.0864,0.03053]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_to_entry","phase_type":"approach","tcp_position_centroid":[0.4998,0.19977,0.29604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.5069,0.06305,0.00938],"force_p95":0.55043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55119,"mean_force":0.54657,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49641,0.10785,0.03981]}],"total_contact_groups":10},"final_pose_error":0.05456,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50745,-0.08291,0.03546],"final_tcp_position":[0.50085,-0.05379,0.02923],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3919.09778,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54678,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":931.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49629,0.10901,0.04197],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":32.0,"n_steps_budget":600.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.54628,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32.0,"raw_peak_contact_force":0.55119,"subtask_id":"approach","tcp_end":[0.49751,0.10662,0.03715],"tcp_start":[0.49629,0.10901,0.04197],"tcp_to_object_dist_end":0.04462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":720.0,"object_pos_end":[0.50699,0.05462,0.03558],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.13488,"object_to_goal_dist_start":0.14321,"object_z_max":0.03569,"peak_contact_force":3919.09778,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":642.0,"raw_peak_contact_force":5.30185,"subtask_id":"contact","tcp_end":[0.49923,0.08381,0.03025],"tcp_start":[0.49751,0.10662,0.03715],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.50743,-0.08272,0.03552],"object_pos_start":[0.50699,0.05462,0.03558],"object_to_goal_dist_end":0.00909,"object_to_goal_dist_start":0.13488,"object_z_max":0.03615,"peak_contact_force":16.73448,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1160.0,"raw_peak_contact_force":38.96253,"subtask_id":"push","tcp_end":[0.50085,-0.05379,0.02923],"tcp_start":[0.50089,-0.05374,0.02928],"tcp_to_object_dist_end":0.03032,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```